"""
任务解析器单元测试
"""
import pytest
from app.utils.task_parser import (
    parse_natural_language_task,
    extract_datetime,
    extract_priority,
    extract_category,
    extract_tags,
    clean_title
)


class TestExtractDatetime:
    """日期提取测试"""

    def test_tomorrow(self):
        """测试明天日期提取"""
        result = extract_datetime("明天下午3点")
        assert result is not None

    def test_today(self):
        """测试今天日期提取"""
        result = extract_datetime("今天截止")
        assert result is not None

    def test_next_week(self):
        """测试下周日期提取"""
        result = extract_datetime("下周三考试")
        assert result is not None

    def test_no_date(self):
        """测试无日期情况"""
        result = extract_datetime("完成作业")
        # dateparser 可能返回 None 或解析出日期
        # 这里主要测试不抛异常


class TestExtractPriority:
    """优先级提取测试"""

    def test_urgent(self):
        """测试紧急优先级"""
        assert extract_priority("紧急任务") == "urgent"
        assert extract_priority("马上完成") == "urgent"
        assert extract_priority("deadline 今天") == "urgent"

    def test_low(self):
        """测试低优先级"""
        assert extract_priority("有空的时候做") == "low"
        assert extract_priority("以后再做") == "low"

    def test_medium(self):
        """测试中等优先级"""
        assert extract_priority("完成作业") == "medium"
        assert extract_priority("准备考试") == "medium"


class TestExtractCategory:
    """分类提取测试"""

    def test_homework(self):
        """测试作业分类"""
        assert extract_category("完成数学作业") == "homework"
        assert extract_category("交 assignment") == "homework"

    def test_exam(self):
        """测试考试分类"""
        assert extract_category("期中考试") == "exam"
        assert extract_category("准备 quiz") == "exam"

    def test_project(self):
        """测试项目分类"""
        assert extract_category("完成项目") == "project"
        assert extract_category("大作业") == "homework"  # "大作业" contains "作业"

    def test_review(self):
        """测试复习分类"""
        assert extract_category("复习英语") == "review"
        assert extract_category("预习物理") == "review"

    def test_general(self):
        """测试通用分类"""
        assert extract_category("买东西") == "general"


class TestExtractTags:
    """标签提取测试"""

    def test_math_tag(self):
        """测试数学标签"""
        tags = extract_tags("完成数学作业")
        assert "math" in tags

    def test_english_tag(self):
        """测试英语标签"""
        tags = extract_tags("复习英语单词")
        assert "english" in tags

    def test_physics_tag(self):
        """测试物理标签"""
        tags = extract_tags("物理实验报告")
        assert "physics" in tags

    def test_multiple_tags(self):
        """测试多标签"""
        tags = extract_tags("数学和物理作业")
        assert "math" in tags
        assert "physics" in tags

    def test_no_tags(self):
        """测试无标签"""
        tags = extract_tags("完成任务")
        assert len(tags) == 0


class TestCleanTitle:
    """标题清理测试"""

    def test_remove_time(self):
        """测试移除时间信息"""
        title = clean_title("明天下午3点前完成数学作业")
        assert "明天" not in title
        assert "3点" not in title

    def test_preserve_content(self):
        """测试保留核心内容"""
        title = clean_title("完成数学作业")
        assert "数学作业" in title


class TestParseNaturalLanguageTask:
    """完整任务解析测试"""

    def test_homework_task(self):
        """测试作业任务解析"""
        result = parse_natural_language_task("明天下午3点前完成数学作业，很重要")
        assert result["title"] is not None
        assert result["priority"] in ["low", "medium", "high", "urgent"]
        assert result["category"] in ["homework", "exam", "project", "review", "general"]
        assert isinstance(result["tags"], list)

    def test_exam_task(self):
        """测试考试任务解析"""
        result = parse_natural_language_task("下周三物理期中考试")
        assert result["category"] == "exam"
        assert "physics" in result["tags"]

    def test_review_task(self):
        """测试复习任务解析"""
        result = parse_natural_language_task("有空复习英语单词")
        assert result["category"] == "review"
        assert result["priority"] == "low"
        assert "english" in result["tags"]

    def test_default_values(self):
        """测试默认值"""
        result = parse_natural_language_task("完成任务")
        assert result["title"] is not None
        assert result["priority"] == "medium"
        assert result["category"] == "general"
        assert isinstance(result["tags"], list)
