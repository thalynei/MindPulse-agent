"""
Pytest 配置文件
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_task():
    """示例任务数据"""
    return {
        "task_description": "明天下午3点前完成数学作业"
    }


@pytest.fixture
def sample_tasks():
    """示例批量任务数据"""
    return [
        "明天交数学作业",
        "下周三期中考试",
        "有空复习英语"
    ]


@pytest.fixture
def sample_note():
    """示例笔记数据"""
    return {
        "note_content": "# 量子力学基本原理\n今天的课程内容是关于量子力学的基本原理，包括波粒二象性和不确定性原理。"
    }
