"""
笔记解析工具 - 规则降级方案
"""
import re
from typing import Dict, List


def generate_note_summary(note_content: str) -> Dict[str, str]:
    """
    笔记摘要规则解析主入口
    """
    return {
        "title": extract_note_title(note_content),
        "summary": extract_note_summary(note_content),
        "tags": extract_note_tags(note_content)
    }


def extract_note_title(content: str) -> str:
    """
    从笔记内容提取标题
    """
    if not content or not content.strip():
        return "无标题笔记"

    lines = content.strip().split('\n')
    first_line = lines[0].strip()

    # Markdown 标题
    if first_line.startswith('#'):
        title = re.sub(r'^#+\s*', '', first_line)
        return title[:50] if len(title) > 50 else title

    # 第一句话
    match = re.search(r'[。！？\n]', first_line)
    if match:
        title = first_line[:match.start()]
    else:
        title = first_line

    if len(title) > 50:
        title = title[:50] + "..."

    return title.strip() or "无标题笔记"


def extract_note_summary(content: str) -> str:
    """
    基于规则生成笔记摘要
    """
    if not content or not content.strip():
        return "空笔记"

    # 去除 Markdown 格式
    cleaned = re.sub(r'[#*`\-\[\]()>]', '', content)
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = cleaned.strip()

    if len(cleaned) <= 200:
        return cleaned

    # 截取前200字符，在句子边界截断
    truncated = cleaned[:200]
    last_period = max(
        truncated.rfind('。'),
        truncated.rfind('！'),
        truncated.rfind('？'),
        truncated.rfind('. ')
    )
    if last_period > 50:
        return truncated[:last_period + 1]

    return truncated + "..."


def extract_note_tags(content: str) -> str:
    """
    提取笔记标签，返回逗号分隔字符串
    """
    tags: List[str] = []
    content_lower = content.lower()

    subjects = [
        ('math', ['数学', 'math', '代数', '几何', '微积分']),
        ('english', ['英语', 'english', '英文']),
        ('chinese', ['语文', '中文', 'chinese']),
        ('physics', ['物理', 'physics', '量子', 'quantum']),
        ('chemistry', ['化学', 'chemistry']),
        ('biology', ['生物', 'biology']),
        ('computer', ['计算机', '编程', 'code', 'programming', 'cs', '算法', 'algorithm']),
        ('history', ['历史', 'history']),
        ('geography', ['地理', 'geography']),
        ('ai', ['人工智能', '机器学习', '深度学习', 'ai', 'machine learning']),
        ('literature', ['文学', '诗词', '小说', '散文']),
        ('economics', ['经济', '金融', 'finance', 'economics']),
    ]

    for tag, keywords in subjects:
        if any(keyword in content_lower for keyword in keywords):
            tags.append(tag)

    return ",".join(tags)


if __name__ == "__main__":
    test_notes = [
        "# 量子力学基本原理\n今天的课程内容是关于量子力学的基本原理，包括波粒二象性和不确定性原理。",
        "数学课笔记：微积分的基本概念，导数和积分的关系。",
        "",
        "短笔记"
    ]
    for note in test_notes:
        result = generate_note_summary(note)
        print(f"内容: {note[:30]}...")
        print(f"结果: {result}")
        print("-" * 50)
