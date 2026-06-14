"""
API v1 路由定义
"""
from fastapi import APIRouter
from app.api.v1.endpoints import tasks
from app.api.v1.endpoints import notes
from app.api.v1.endpoints import study_insight

api_router = APIRouter()

# 注册任务分析API端点
api_router.include_router(tasks.router, prefix="/analyze", tags=["task-analysis"])

# 注册笔记摘要API端点
api_router.include_router(notes.router, prefix="/analyze", tags=["note-summary"])

# 注册学习洞察API端点
api_router.include_router(study_insight.router, prefix="/analyze", tags=["study-insight"])