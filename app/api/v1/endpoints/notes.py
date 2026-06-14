"""
笔记摘要API端点
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.agents.note_summarizer import note_summarizer_agent

router = APIRouter()


class NoteSummaryRequest(BaseModel):
    """笔记摘要请求模型"""
    note_content: str = Field(..., max_length=50000)


class NoteSummaryResponse(BaseModel):
    """笔记摘要响应模型"""
    title: str
    summary: str
    tags: str


@router.post("/generate_summary", response_model=NoteSummaryResponse, summary="生成笔记摘要")
async def generate_note_summary(request: NoteSummaryRequest):
    """
    接收笔记内容，返回AI生成的摘要
    由Java后端调用此接口获取笔记摘要
    """
    try:
        # 输入校验
        if not request.note_content or not request.note_content.strip():
            return NoteSummaryResponse(
                title="无标题笔记",
                summary="空笔记",
                tags=""
            )

        # 使用AI生成摘要
        result = await note_summarizer_agent.generate_summary(request.note_content)

        return NoteSummaryResponse(
            title=result["title"],
            summary=result["summary"],
            tags=result["tags"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"笔记摘要生成失败: {str(e)}"
        )
