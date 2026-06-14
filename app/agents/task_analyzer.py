"""
任务分析智能体
"""
import logging
from typing import Dict, Any
from app.core.config import settings
from app.core.ollama_client import ollama_client
from app.utils.task_parser import parse_natural_language_task

logger = logging.getLogger(__name__)


class TaskAnalyzerAgent:
    """任务分析智能体"""

    async def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """使用 Ollama 分析任务描述，失败时降级到规则解析。"""
        if not settings.OLLAMA_ENABLED:
            return parse_natural_language_task(task_description)

        prompt = f"""请分析以下任务描述并提取相关信息：

任务描述: {task_description}

请返回JSON格式的结果，包含以下字段：
- title: 任务标题
- due_date: 截止日期（ISO格式，如果无法确定则为空）
- priority: 优先级（low, medium, high, urgent之一）
- category: 任务分类（如：作业、复习、考试、项目等）
- estimated_duration: 预估完成时间（分钟，如果无法确定则为null）
- tags: 相关标签列表

请确保返回纯JSON格式，不要包含其他说明文字。"""

        try:
            parsed = await ollama_client.generate_json(prompt, timeout=settings.OLLAMA_TIMEOUT)
            if parsed and "title" in parsed:
                return parsed
        except Exception as e:
            logger.error("Ollama analysis failed: %s, falling back to rule-based parsing", e)

        return parse_natural_language_task(task_description)


task_analyzer_agent = TaskAnalyzerAgent()
