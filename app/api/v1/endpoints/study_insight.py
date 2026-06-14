"""
Study insight API endpoint - provides AI-powered study insights.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel, Field
from app.agents.study_insight_agent import study_insight_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class StudyInsightRequest(BaseModel):
    """Study insight request model."""
    sessions: list[dict[str, Any]] = Field(..., max_length=100)
    tasks: list[dict[str, Any]] = Field(..., max_length=100)


class StudyInsightResponse(BaseModel):
    """Study insight response model."""
    insights: list[str]
    recommendations: list[str]


@router.post("/study-insight", response_model=StudyInsightResponse, summary="Generate study insights")
async def generate_study_insight(request: StudyInsightRequest):
    """
    Receive study session and task data, return AI-generated insights and recommendations.
    Called by the Java backend to provide study analysis.
    """
    try:
        result = await study_insight_agent.generate_insights(request.sessions, request.tasks)
        return StudyInsightResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study insights: {str(e)}"
        )
