"""
笔记解析器单元测试
"""
import pytest
from app.utils.note_parser import (
    generate_note_summary,
    extract_note_title,
    extract_note_summary,
    extract_note_tags
)


class TestExtractNoteTitle:
    """标题提取测试"""

    def test_markdown_title(self):
        """测试 Markdown 标题"""
        title = extract_note_title("# 量子力学笔记\n内容...")
        assert title == "量子力学笔记"

    def test_plain_first_line(self):
        """测试纯文本首行"""
        title = extract_note_title("今天的课程内容很有趣。第二行")
        assert "今天的课程内容很有趣" in title

    def test_empty_content(self):
        """测试空内容"""
        assert extract_note_title("") == "无标题笔记"
        assert extract_note_title(None) == "无标题笔记"

    def test_long_title_truncation(self):
        """测试长标题截断"""
        long_content = "这是一段非常非常长的标题超过了五十个字符应该被截断处理"
        title = extract_note_title(long_content)
        assert len(title) <= 53  # 50 + "..."


class TestExtractNoteSummary:
    """摘要生成测试"""

    def test_short_content(self):
        """测试短内容直接返回"""
        summary = extract_note_summary("短笔记内容")
        assert summary == "短笔记内容"

    def test_long_content_truncation(self):
        """测试长内容截断"""
        long_content = "这是一段测试内容。" * 50
        summary = extract_note_summary(long_content)
        assert len(summary) <= 200

    def test_markdown_stripping(self):
        """测试去除 Markdown 格式"""
        summary = extract_note_summary("# 标题\n- 列表项\n**粗体**内容")
        assert "#" not in summary
        assert "**" not in summary

    def test_empty_content(self):
        """测试空内容"""
        assert extract_note_summary("") == "空笔记"


class TestExtractNoteTags:
    """标签提取测试"""

    def test_physics_tag(self):
        """测试物理标签"""
        tags = extract_note_tags("量子力学基本原理")
        assert "physics" in tags

    def test_multiple_tags(self):
        """测试多标签"""
        tags = extract_note_tags("数学和物理的交叉学科")
        assert "math" in tags
        assert "physics" in tags
        assert "," in tags

    def test_no_tags(self):
        """测试无标签"""
        tags = extract_note_tags("今天天气很好")
        assert tags == ""

    def test_returns_string(self):
        """测试返回字符串格式"""
        tags = extract_note_tags("数学课笔记")
        assert isinstance(tags, str)


class TestGenerateNoteSummary:
    """完整摘要测试"""

    def test_full_note(self):
        """测试完整笔记解析"""
        note = "# 量子力学\n今天的课程讲解了波粒二象性。"
        result = generate_note_summary(note)
        assert "title" in result
        assert "summary" in result
        assert "tags" in result
        assert isinstance(result["tags"], str)

    def test_empty_note(self):
        """测试空笔记"""
        result = generate_note_summary("")
        assert result["title"] == "无标题笔记"
        assert result["summary"] == "空笔记"
