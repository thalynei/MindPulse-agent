"""
学习洞察智能体单元测试
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.study_insight_agent import StudyInsightAgent


@pytest.fixture
def agent():
    return StudyInsightAgent()


class TestStudyInsightAgent:
    """学习洞察智能体测试"""

    @pytest.mark.asyncio
    async def test_ollama_success(self, agent):
        """测试 Ollama 成功返回"""
        mock_result = {
            "insights": ["You studied 2 hours", "Good completion rate"],
            "recommendations": ["Keep it up"]
        }
        sessions = [{"actualMinutes": 120, "status": "completed", "startTime": "2026-01-01T09:00:00"}]

        with patch("app.agents.study_insight_agent.ollama_client") as mock_client, \
             patch("app.agents.study_insight_agent.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_insights(sessions, [])

        assert result["insights"] == ["You studied 2 hours", "Good completion rate"]
        assert result["recommendations"] == ["Keep it up"]

    @pytest.mark.asyncio
    async def test_ollama_failure_fallback(self, agent):
        """测试 Ollama 失败时降级"""
        sessions = [{"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"}]

        with patch("app.agents.study_insight_agent.ollama_client") as mock_client, \
             patch("app.agents.study_insight_agent.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(side_effect=Exception("Error"))
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_insights(sessions, [])

        assert "insights" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_ollama_disabled(self, agent):
        """测试 Ollama 未启用"""
        sessions = [{"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"}]

        with patch("app.agents.study_insight_agent.settings") as mock_settings:
            mock_settings.OLLAMA_ENABLED = False
            result = await agent.generate_insights(sessions, [])

        assert "insights" in result

    @pytest.mark.asyncio
    async def test_ollama_missing_fields(self, agent):
        """测试 Ollama 返回缺少字段"""
        mock_result = {"insights": ["test"]}  # 缺少 recommendations

        with patch("app.agents.study_insight_agent.ollama_client") as mock_client, \
             patch("app.agents.study_insight_agent.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=mock_result)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_insights([], [])

        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_ollama_returns_none(self, agent):
        """测试 Ollama 返回 None"""
        with patch("app.agents.study_insight_agent.ollama_client") as mock_client, \
             patch("app.agents.study_insight_agent.settings") as mock_settings:
            mock_client.generate_json = AsyncMock(return_value=None)
            mock_settings.OLLAMA_ENABLED = True
            mock_settings.OLLAMA_TIMEOUT = 30
            result = await agent.generate_insights([], [])

        assert "insights" in result

    def test_build_prompt(self, agent):
        """测试 prompt 构建"""
        sessions = [{"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"}]
        tasks = [{"status": "completed"}]
        prompt = agent._build_prompt(sessions, tasks)
        assert "Total sessions: 1" in prompt
        assert "Completed: 1" in prompt
        assert "JSON" in prompt
