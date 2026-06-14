"""
API 端点集成测试
"""
import pytest
from fastapi.testclient import TestClient


class TestAnalyzeTask:
    """任务分析端点测试"""

    def test_analyze_task_success(self, client: TestClient, sample_task):
        """测试任务分析成功"""
        response = client.post("/api/v1/analyze/task", json=sample_task)
        assert response.status_code == 200
        data = response.json()
        assert "original_description" in data
        assert "analyzed_task" in data
        assert data["original_description"] == sample_task["task_description"]

    def test_analyze_task_structure(self, client: TestClient, sample_task):
        """测试任务分析返回结构"""
        response = client.post("/api/v1/analyze/task", json=sample_task)
        data = response.json()
        analyzed = data["analyzed_task"]
        assert "title" in analyzed
        assert "due_date" in analyzed
        assert "priority" in analyzed
        assert "category" in analyzed
        assert "tags" in analyzed

    def test_analyze_task_empty_description(self, client: TestClient):
        """测试空描述"""
        response = client.post("/api/v1/analyze/task", json={"task_description": ""})
        # 应该仍然返回 200，使用规则解析
        assert response.status_code == 200

    def test_analyze_task_invalid_json(self, client: TestClient):
        """测试无效 JSON"""
        response = client.post(
            "/api/v1/analyze/task",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestBatchAnalyze:
    """批量分析端点测试"""

    def test_batch_analyze_success(self, client: TestClient, sample_tasks):
        """测试批量分析成功"""
        response = client.post("/api/v1/analyze/batch-analyze", json=sample_tasks)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == len(sample_tasks)

    def test_batch_analyze_structure(self, client: TestClient, sample_tasks):
        """测试批量分析返回结构"""
        response = client.post("/api/v1/analyze/batch-analyze", json=sample_tasks)
        data = response.json()
        for result in data["results"]:
            assert "original_description" in result
            assert "analyzed_task" in result

    def test_batch_analyze_empty_list(self, client: TestClient):
        """测试空列表"""
        response = client.post("/api/v1/analyze/batch-analyze", json=[])
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0


class TestGenerateSummary:
    """笔记摘要端点测试"""

    def test_generate_summary_success(self, client: TestClient):
        """测试笔记摘要成功"""
        response = client.post("/api/v1/analyze/generate_summary", json={
            "note_content": "# 量子力学\n波粒二象性是量子力学的基础。"
        })
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "summary" in data
        assert "tags" in data
        assert isinstance(data["tags"], str)

    def test_generate_summary_empty_content(self, client: TestClient):
        """测试空内容"""
        response = client.post("/api/v1/analyze/generate_summary", json={
            "note_content": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "无标题笔记"

    def test_generate_summary_invalid_json(self, client: TestClient):
        """测试无效 JSON"""
        response = client.post(
            "/api/v1/analyze/generate_summary",
            content="invalid",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_generate_summary_long_content(self, client: TestClient):
        """测试长内容不崩溃"""
        long_note = "这是一段很长的笔记内容。" * 500
        response = client.post("/api/v1/analyze/generate_summary", json={
            "note_content": long_note
        })
        assert response.status_code == 200


class TestRootEndpoint:
    """根端点测试"""

    def test_root(self, client: TestClient):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "MindPulse" in data["message"]

    def test_health(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestStudyInsight:
    """学习洞察端点测试"""

    def test_study_insight_success(self, client: TestClient):
        """测试学习洞察成功"""
        response = client.post("/api/v1/analyze/study-insight", json={
            "sessions": [
                {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"}
            ],
            "tasks": []
        })
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert "recommendations" in data
        assert isinstance(data["insights"], list)
        assert isinstance(data["recommendations"], list)

    def test_study_insight_empty_data(self, client: TestClient):
        """测试空数据"""
        response = client.post("/api/v1/analyze/study-insight", json={
            "sessions": [],
            "tasks": []
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["insights"]) > 0

    def test_study_insight_invalid_json(self, client: TestClient):
        """测试无效 JSON"""
        response = client.post(
            "/api/v1/analyze/study-insight",
            content="invalid",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
