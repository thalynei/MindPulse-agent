"""
笔记摘要智能体
"""
import logging
from typing import Dict, Any
from app.core.config import settings
from app.core.ollama_client import ollama_client
from app.utils.note_parser import generate_note_summary

logger = logging.getLogger(__name__)


class NoteSummarizerAgent:
    """笔记摘要智能体"""

    async def generate_summary(self, note_content: str) -> Dict[str, str]:
        """使用 Ollama 生成笔记摘要，失败时降级到规则解析。"""
        if not settings.OLLAMA_ENABLED:
            return generate_note_summary(note_content)

        truncated_content = self._truncate_content(note_content, max_chars=2000)

        prompt = f"""请对以下笔记内容生成摘要。

笔记内容:
{truncated_content}

请返回JSON格式的结果，包含以下字段：
- title: 笔记标题（简短，不超过30字）
- summary: 笔记摘要（2-3句话，概括核心内容）
- tags: 相关标签（逗号分隔的英文标签，如 physics,quantum）

请确保返回纯JSON格式，不要包含其他说明文字。"""

        try:
            parsed = await ollama_client.generate_json(prompt, timeout=settings.OLLAMA_TIMEOUT)
            if parsed:
                if "title" not in parsed or not parsed["title"]:
                    parsed["title"] = self._quick_title(note_content)
                if "summary" not in parsed or not parsed["summary"]:
                    parsed["summary"] = note_content[:200]
                if "tags" not in parsed:
                    parsed["tags"] = ""
                if isinstance(parsed["tags"], list):
                    parsed["tags"] = ",".join(parsed["tags"])
                return parsed
        except Exception as e:
            logger.error("Ollama summary generation failed: %s, falling back to rule-based parsing", e)

        return generate_note_summary(note_content)

    def _truncate_content(self, content: str, max_chars: int = 2000) -> str:
        """截断长笔记，在句子边界截断。"""
        if len(content) <= max_chars:
            return content

        truncated = content[:max_chars]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？')
        )
        if last_period > max_chars // 2:
            return truncated[:last_period + 1]

        return truncated

    def _quick_title(self, content: str) -> str:
        """快速提取标题（兜底用）。"""
        first_line = content.strip().split('\n')[0].strip()
        title = first_line[:30]
        return title if title else "无标题笔记"


note_summarizer_agent = NoteSummarizerAgent()
