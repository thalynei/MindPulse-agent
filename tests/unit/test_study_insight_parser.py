"""
学习洞察解析器单元测试
"""
import pytest
from app.utils.study_insight_parser import generate_study_insights, _get_hour


class TestGenerateStudyInsights:
    """学习洞察生成测试"""

    def test_empty_sessions(self):
        """测试空会话列表"""
        result = generate_study_insights([], [])
        assert "insights" in result
        assert "recommendations" in result
        assert len(result["insights"]) > 0
        assert "No study sessions" in result["insights"][0]

    def test_high_study_time(self):
        """测试高学习时长"""
        sessions = [
            {"actualMinutes": 120, "status": "completed", "startTime": "2026-01-01T09:00:00"},
            {"actualMinutes": 120, "status": "completed", "startTime": "2026-01-01T14:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert any("4.0 hours" in i for i in result["insights"])

    def test_low_study_time(self):
        """测试低学习时长"""
        sessions = [
            {"actualMinutes": 30, "status": "completed", "startTime": "2026-01-01T09:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert any("30 minutes" in i for i in result["insights"])

    def test_high_completion_rate(self):
        """测试高完成率"""
        sessions = [
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"},
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T10:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert any("100%" in i for i in result["insights"])

    def test_low_completion_rate(self):
        """测试低完成率"""
        sessions = [
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"},
            {"actualMinutes": 60, "status": "cancelled", "startTime": "2026-01-01T10:00:00"},
            {"actualMinutes": 60, "status": "cancelled", "startTime": "2026-01-01T11:00:00"},
            {"actualMinutes": 60, "status": "cancelled", "startTime": "2026-01-01T12:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert any("25%" in i for i in result["insights"])

    def test_morning_productivity(self):
        """测试上午高效时段"""
        sessions = [
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"},
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T10:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert any("morning" in i for i in result["insights"])

    def test_task_completion_low(self):
        """测试任务完成率低"""
        sessions = [{"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"}]
        tasks = [
            {"status": "completed"},
            {"status": "pending"},
            {"status": "pending"},
        ]
        result = generate_study_insights(sessions, tasks)
        assert any("Focus on completing" in r for r in result["recommendations"])

    def test_camel_case_fields(self):
        """测试 camelCase 字段名"""
        sessions = [
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"},
        ]
        result = generate_study_insights(sessions, [])
        assert "insights" in result


class TestGetHour:
    """时间提取测试"""

    def test_valid_time(self):
        """测试有效时间"""
        session = {"startTime": "2026-01-01T14:30:00"}
        assert _get_hour(session) == 14

    def test_camel_case_start_time(self):
        """测试 camelCase startTime"""
        session = {"startTime": "2026-01-01T09:00:00"}
        assert _get_hour(session) == 9

    def test_missing_time(self):
        """测试缺失时间"""
        session = {}
        assert _get_hour(session) == 12  # default to noon

    def test_invalid_time_format(self):
        """测试无效时间格式"""
        session = {"startTime": "invalid"}
        assert _get_hour(session) == 12
