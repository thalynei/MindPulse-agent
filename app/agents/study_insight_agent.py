"""
Study insight agent - generates insights from study session data.
Uses Ollama for AI analysis with rule-based fallback.
"""
import json
import logging
from typing import Any
from app.core.config import settings
from app.core.ollama_client import ollama_client
from app.utils.study_insight_parser import generate_study_insights

logger = logging.getLogger(__name__)


class StudyInsightAgent:
    """Study insight agent with Ollama integration and rule-based fallback."""

    async def generate_insights(self, sessions: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate study insights using Ollama, falling back to rule-based analysis."""
        if not settings.OLLAMA_ENABLED:
            return generate_study_insights(sessions, tasks)

        prompt = self._build_prompt(sessions, tasks)

        try:
            parsed = await ollama_client.generate_json(prompt, timeout=settings.OLLAMA_TIMEOUT)
            if parsed and "insights" in parsed and "recommendations" in parsed:
                return parsed
        except Exception as e:
            logger.error("Ollama call failed for study insights: %s, falling back to rule-based parsing", e)

        return generate_study_insights(sessions, tasks)

    def _build_prompt(self, sessions: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> str:
        """Build the prompt for Ollama."""
        session_summary = f"Total sessions: {len(sessions)}, "
        completed = sum(1 for s in sessions if s.get("status") == "completed")
        session_summary += f"Completed: {completed}"

        sessions_json = json.dumps(sessions[:10], default=str, ensure_ascii=False)
        tasks_json = json.dumps(tasks[:10], default=str, ensure_ascii=False)

        return f"""Based on the following study data, provide insights and recommendations in JSON format.

Study Data: {session_summary}
Sessions: {sessions_json}
Tasks: {tasks_json}

Respond with pure JSON only:
{{"insights": ["insight 1", "insight 2"], "recommendations": ["recommendation 1", "recommendation 2"]}}"""


study_insight_agent = StudyInsightAgent()
