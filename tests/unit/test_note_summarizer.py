"""
笔记摘要智能体单元测试
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.note_summarizer import NoteSummarizerAgent


@pytest.fixture
def agent():
    return NoteSummarizerAgent()


class TestNoteSummarizerAgent:
    """笔记摘要智能体测试"""

    @pytest.mark.asyncio
    async def test_ollama_success(self, agent):
        """测试 Ollama 成功返回"""
        mock_result = {
            "title": "量子力学笔记",
            "summary": "本文介绍了量子力学的基础概念。",
            "tags": "physics,quantum"
        }
        with patch("app.agents.note_summarizer.ollama_client") as mock_client, \
             patch("app.agents.note_summarizer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_summary("# 量子力学\n波粒二象性")

        assert result["title"] == "量子力学笔记"
        assert result["tags"] == "physics,quantum"

    @pytest.mark.asyncio
    async def test_ollama_failure_fallback(self, agent):
        """测试 Ollama 失败时降级"""
        with patch("app.agents.note_summarizer.ollama_client") as mock_client, \
             patch("app.agents.note_summarizer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(side_effect=Exception("Timeout"))
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_summary("# 物理笔记\n力学基础")

        assert result["title"] is not None
        assert result["summary"] is not None

    @pytest.mark.asyncio
    async def test_ollama_disabled(self, agent):
        """测试 Ollama 未启用"""
        with patch("app.agents.note_summarizer.settings") as mock_settings:
            mock_settings.OLLAMA_ENABLED = False
            result = await agent.generate_summary("# 数学笔记\n微积分")

        assert result["title"] is not None
        assert result["tags"] is not None

    @pytest.mark.asyncio
    async def test_tags_list_to_string(self, agent):
        """测试 tags 从列表转为字符串"""
        mock_result = {
            "title": "笔记",
            "summary": "摘要",
            "tags": ["physics", "quantum"]
        }
        with patch("app.agents.note_summarizer.ollama_client") as mock_client, \
             patch("app.agents.note_summarizer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_summary("测试内容")

        assert isinstance(result["tags"], str)
        assert "physics" in result["tags"]

    def test_truncate_short_content(self, agent):
        """测试短内容不截断"""
        content = "短笔记"
        assert agent._truncate_content(content, max_chars=2000) == content

    def test_truncate_long_content(self, agent):
        """测试长内容截断"""
        content = "这是一段很长的笔记。" * 200
        result = agent._truncate_content(content, max_chars=2000)
        assert len(result) <= 2000

    def test_quick_title(self, agent):
        """测试快速标题提取"""
        assert agent._quick_title("第一行标题\n第二行") == "第一行标题"
        assert agent._quick_title("") == "无标题笔记"
