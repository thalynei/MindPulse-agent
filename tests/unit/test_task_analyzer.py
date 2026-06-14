"""
任务分析智能体单元测试
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.task_analyzer import TaskAnalyzerAgent


@pytest.fixture
def agent():
    return TaskAnalyzerAgent()


class TestTaskAnalyzerAgent:
    """任务分析智能体测试"""

    @pytest.mark.asyncio
    async def test_ollama_success(self, agent):
        """测试 Ollama 成功返回"""
        mock_result = {
            "title": "完成数学作业",
            "due_date": "2026-06-10T15:00:00",
            "priority": "high",
            "category": "homework",
            "tags": ["math"]
        }
        with patch("app.agents.task_analyzer.ollama_client") as mock_client, \
             patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.analyze_task("明天下午3点前完成数学作业")

        assert result["title"] == "完成数学作业"
        assert result["priority"] == "high"

    @pytest.mark.asyncio
    async def test_ollama_failure_fallback(self, agent):
        """测试 Ollama 失败时降级到规则解析"""
        with patch("app.agents.task_analyzer.ollama_client") as mock_client, \
             patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(side_effect=Exception("Connection failed"))
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.analyze_task("明天下午3点前完成数学作业")

        assert result["title"] is not None
        assert result["priority"] in ["low", "medium", "high", "urgent"]

    @pytest.mark.asyncio
    async def test_ollama_disabled(self, agent):
        """测试 Ollama 未启用时使用规则解析"""
        with patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_settings.OLLAMA_ENABLED = False
            result = await agent.analyze_task("紧急考试")

        assert result["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_ollama_returns_no_title(self, agent):
        """测试 Ollama 返回缺少 title 的结果"""
        mock_result = {"priority": "high", "category": "exam"}
        with patch("app.agents.task_analyzer.ollama_client") as mock_client, \
             patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.analyze_task("期中考试")

        assert result["title"] is not None

    @pytest.mark.asyncio
    async def test_ollama_returns_none(self, agent):
        """测试 Ollama 返回 None"""
        with patch("app.agents.task_analyzer.ollama_client") as mock_client, \
             patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=None)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.analyze_task("完成作业")

        assert result["title"] is not None

    @pytest.mark.asyncio
    async def test_ollama_no_title_fallback(self, agent):
        """测试 Ollama 返回无 title 时降级"""
        with patch("app.agents.task_analyzer.ollama_client") as mock_client, \
             patch("app.agents.task_analyzer.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value={"tags": ["math"]})
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.analyze_task("明天交数学作业")

        assert result["title"] is not None
