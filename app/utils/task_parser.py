"""
任务解析工具
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import dateparser


def parse_natural_language_task(task_description: str) -> Dict[str, Any]:
    """
    解析自然语言任务描述
    """
    result = {
        "title": task_description,
        "due_date": None,
        "priority": "medium",
        "category": "general",
        "estimated_duration": None,
        "tags": []
    }
    
    # 解析截止时间
    due_date = extract_datetime(task_description)
    if due_date:
        result["due_date"] = due_date.isoformat()
    
    # 解析优先级
    result["priority"] = extract_priority(task_description)
    
    # 解析类别
    result["category"] = extract_category(task_description)
    
    # 提取标签
    result["tags"] = extract_tags(task_description)
    
    # 设置标题（去除时间信息）
    result["title"] = clean_title(task_description, due_date)
    
    return result


def extract_datetime(text: str) -> Optional[datetime]:
    """
    从文本中提取日期时间
    """
    # 使用dateparser来解析自然语言日期
    parsed_date = dateparser.parse(
        text,
        settings={
            'PREFER_DATES_FROM': 'future',
            'DATE_ORDER': 'YMD'
        }
    )
    
    # 如果dateparser没有解析到日期，尝试正则表达式
    if not parsed_date:
        # 匹配常见的时间表达式
        time_patterns = [
            r'今天', r'明天', r'后天',
            r'本周', r'下周', r'这周', r'下周',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}[-/]\d{1,2}',
            r'(?:上午|下午|晚上)?\d{1,2}:\d{2}',
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text):
                # 对于模糊的时间表达，可以根据上下文推测
                if '明天' in text:
                    return datetime.now() + timedelta(days=1)
                elif '今天' in text:
                    return datetime.now().replace(hour=23, minute=59)  # 设为今天结束
                elif '后天' in text:
                    return datetime.now() + timedelta(days=2)
                elif '下周' in text or '下一周' in text:
                    return datetime.now() + timedelta(weeks=1)
    
    return parsed_date


def extract_priority(text: str) -> str:
    """
    从文本中提取优先级
    """
    text_lower = text.lower()
    
    # 高优先级关键词
    urgent_keywords = [
        '紧急', '急', '马上', '立刻', '尽快', 'deadline', '截止', 
        '重要', '关键', '必须', '务必', 'today', 'urgent'
    ]
    
    # 低优先级关键词
    low_keywords = [
        '有空', '有时间', '闲暇', '以后', '之后', 'later'
    ]
    
    # 检查紧急关键词
    for keyword in urgent_keywords:
        if keyword in text_lower:
            return 'urgent'
    
    # 检查低优先级关键词
    for keyword in low_keywords:
        if keyword in text_lower:
            return 'low'
    
    # 默认中等优先级
    return 'medium'


def extract_category(text: str) -> str:
    """
    从文本中提取类别
    """
    text_lower = text.lower()
    
    # 学业类别关键词（更具体的关键词放在前面）
    homework_keywords = ['作业', 'assignment', 'homework', '习题']
    exam_keywords = ['考试', '测验', 'exam', 'test', 'quiz', '期末']
    project_keywords = ['项目', 'project', '设计']
    review_keywords = ['复习', 'review', '预习', 'study']
    
    if any(keyword in text_lower for keyword in homework_keywords):
        return 'homework'
    elif any(keyword in text_lower for keyword in exam_keywords):
        return 'exam'
    elif any(keyword in text_lower for keyword in project_keywords):
        return 'project'
    elif any(keyword in text_lower for keyword in review_keywords):
        return 'review'
    else:
        return 'general'


def extract_tags(text: str) -> list[str]:
    """
    从文本中提取标签
    """
    tags = []
    text_lower = text.lower()
    
    # 常见学科标签
    subjects = [
        ('math', ['数学', 'math', '代数', '几何', '微积分']),
        ('english', ['英语', 'english', '英文']),
        ('chinese', ['语文', '中文', 'chinese']),
        ('physics', ['物理', 'physics']),
        ('chemistry', ['化学', 'chemistry']),
        ('biology', ['生物', 'biology']),
        ('computer', ['计算机', '编程', 'code', 'programming', 'cs']),
        ('history', ['历史', 'history']),
        ('geography', ['地理', 'geography']),
    ]
    
    for tag, keywords in subjects:
        if any(keyword in text_lower for keyword in keywords):
            tags.append(tag)
    
    return tags


def clean_title(text: str, due_date: Optional[datetime] = None) -> str:
    """
    清理标题，移除时间信息
    """
    # 移除常见的时间表达式
    time_expressions = [
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # 日期
        r'\d{1,2}[-/]\d{1,2}',          # 月日
        r'(?:上午|下午|晚上)?\d{1,2}:\d{2}',  # 时间 (HH:MM)
        r'(?:上午|下午|晚上)?\d{1,2}点(?:\d{1,2}分)?',  # 时间 (X点Y分)
        r'今天', r'明天', r'后天', r'本周', r'下周',
        r'截止', r'之前', r'以前', r'前完成'
    ]
    
    cleaned = text
    for expr in time_expressions:
        cleaned = re.sub(expr, '', cleaned)
    
    # 移除多余的空格
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


# 测试函数
if __name__ == "__main__":
    test_tasks = [
        "明天下午3点前完成数学作业，很重要",
        "下周准备期中考试，物理和化学",
        "有空的时候复习英语单词",
        "尽快完成编程项目"
    ]
    
    for task in test_tasks:
        result = parse_natural_language_task(task)
        print(f"原任务: {task}")
        print(f"解析结果: {result}")
        print("-" * 50)