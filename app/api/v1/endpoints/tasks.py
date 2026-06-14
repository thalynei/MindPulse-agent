"""
任务分析API端点 - 仅提供AI分析功能
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.agents.task_analyzer import task_analyzer_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskAnalysisRequest(BaseModel):
    """
    任务分析请求模型
    """
    task_description: str = Field(..., max_length=2000)


class TaskAnalysisResponse(BaseModel):
    """
    任务分析响应模型
    """
    original_description: str
    analyzed_task: Dict[str, Any]


@router.post("/task", response_model=TaskAnalysisResponse, summary="分析任务描述")
async def analyze_task_description(request: TaskAnalysisRequest):
    """
    接收自然语言任务描述，返回AI分析结果
    由Java后端调用此接口获取任务解析结果
    """
    try:
        # 使用AI分析任务描述
        analysis_result = await task_analyzer_agent.analyze_task(request.task_description)
        
        return TaskAnalysisResponse(
            original_description=request.task_description,
            analyzed_task=analysis_result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务分析失败: {str(e)}"
        )


@router.post("/batch-analyze", summary="批量分析任务")
async def batch_analyze_tasks(descriptions: list[str] = Body(...)):
    """
    批量分析多个任务描述（并发执行）
    """
    async def _analyze_one(desc: str) -> Dict[str, Any]:
        try:
            analysis_result = await task_analyzer_agent.analyze_task(desc)
            return {
                "original_description": desc,
                "analyzed_task": analysis_result
            }
        except Exception as e:
            logger.error("Failed to analyze task '%s': %s", desc, e)
            return {
                "original_description": desc,
                "analyzed_task": {"title": desc, "error": str(e)}
            }

    tasks = [_analyze_one(desc) for desc in descriptions]
    results = await asyncio.gather(*tasks)

    return {"results": results}