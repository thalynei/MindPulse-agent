#!/usr/bin/env python3
"""
MindPulse Agent 全接口测试脚本
覆盖所有API端点，测试正常/边界/错误情况
"""
import argparse
import json
import sys
import time
from typing import Any

import requests

# ANSI颜色码
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# 统计
passed = 0
failed = 0


def print_header(text: str) -> None:
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")


def print_test(name: str) -> None:
    print(f"\n{YELLOW}► {name}{RESET}")


def print_pass(msg: str = "") -> None:
    global passed
    passed += 1
    print(f"  {GREEN}✓ PASS{RESET} {msg}")


def print_fail(msg: str = "") -> None:
    global failed
    failed += 1
    print(f"  {RED}✗ FAIL{RESET} {msg}")


def print_response(resp: requests.Response) -> None:
    print(f"  Status: {resp.status_code}")
    try:
        data = resp.json()
        print(f"  Response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
    except Exception:
        print(f"  Response: {resp.text[:200]}")


def test_root(base_url: str) -> None:
    """测试根路径"""
    print_test("GET / - 欢迎消息")
    resp = requests.get(f"{base_url}/", timeout=10)
    print_response(resp)
    if resp.status_code == 200 and "MindPulse" in resp.json().get("message", ""):
        print_pass("返回欢迎消息")
    else:
        print_fail("未返回正确的欢迎消息")


def test_health(base_url: str) -> None:
    """测试健康检查"""
    print_test("GET /health - 健康检查")
    resp = requests.get(f"{base_url}/health", timeout=10)
    print_response(resp)
    if resp.status_code == 200 and resp.json().get("status") == "ok":
        print_pass("健康检查通过")
    else:
        print_fail("健康检查失败")


def test_analyze_task(base_url: str) -> None:
    """测试单条任务分析"""
    url = f"{base_url}/api/v1/analyze/task"

    # 正常输入
    print_test("POST /api/v1/analyze/task - 正常输入")
    resp = requests.post(url, json={"task_description": "明天下午3点前完成数学作业"}, timeout=30)
    print_response(resp)
    if resp.status_code == 200:
        data = resp.json()
        if "analyzed_task" in data and "title" in data["analyzed_task"]:
            print_pass("返回正确的任务分析结果")
        else:
            print_fail("返回格式不正确")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 空输入
    print_test("POST /api/v1/analyze/task - 空描述")
    resp = requests.post(url, json={"task_description": ""}, timeout=30)
    print_response(resp)
    if resp.status_code == 200:
        print_pass("空描述仍返回200")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 无效JSON
    print_test("POST /api/v1/analyze/task - 无效JSON")
    resp = requests.post(url, data="invalid json", headers={"Content-Type": "application/json"}, timeout=10)
    print_response(resp)
    if resp.status_code == 422:
        print_pass("返回422验证错误")
    else:
        print_fail(f"期望422，实际: {resp.status_code}")


def test_batch_analyze(base_url: str) -> None:
    """测试批量任务分析"""
    url = f"{base_url}/api/v1/analyze/batch-analyze"

    # 正常输入
    print_test("POST /api/v1/analyze/batch-analyze - 正常输入")
    tasks = ["明天交数学作业", "下周三期中考试", "有空复习英语"]
    resp = requests.post(url, json=tasks, timeout=60)
    print_response(resp)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) == 3:
            print_pass(f"返回{len(data['results'])}个结果")
        else:
            print_fail("结果数量不正确")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 空列表
    print_test("POST /api/v1/analyze/batch-analyze - 空列表")
    resp = requests.post(url, json=[], timeout=10)
    print_response(resp)
    if resp.status_code == 200 and len(resp.json().get("results", [])) == 0:
        print_pass("空列表返回空结果")
    else:
        print_fail("空列表处理不正确")


def test_generate_summary(base_url: str) -> None:
    """测试笔记摘要生成"""
    url = f"{base_url}/api/v1/analyze/generate_summary"

    # 正常输入
    print_test("POST /api/v1/analyze/generate_summary - 正常输入")
    note = "# 量子力学基本原理\n今天的课程内容是关于量子力学的基本原理，包括波粒二象性和不确定性原理。"
    resp = requests.post(url, json={"note_content": note}, timeout=30)
    print_response(resp)
    if resp.status_code == 200:
        data = resp.json()
        if all(k in data for k in ["title", "summary", "tags"]):
            print_pass("返回完整的摘要结构")
        else:
            print_fail("缺少必要字段")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 空内容
    print_test("POST /api/v1/analyze/generate_summary - 空内容")
    resp = requests.post(url, json={"note_content": ""}, timeout=10)
    print_response(resp)
    if resp.status_code == 200:
        print_pass("空内容返回200")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 长内容
    print_test("POST /api/v1/analyze/generate_summary - 长内容")
    long_note = "这是一段很长的笔记内容。" * 1000
    resp = requests.post(url, json={"note_content": long_note}, timeout=30)
    print_response(resp)
    if resp.status_code == 200:
        print_pass("长内容不崩溃")
    else:
        print_fail(f"状态码: {resp.status_code}")


def test_study_insight(base_url: str) -> None:
    """测试学习洞察生成"""
    url = f"{base_url}/api/v1/analyze/study-insight"

    # 正常输入
    print_test("POST /api/v1/analyze/study-insight - 正常输入")
    data = {
        "sessions": [
            {"actualMinutes": 60, "status": "completed", "startTime": "2026-01-01T09:00:00"},
            {"actualMinutes": 45, "status": "completed", "startTime": "2026-01-01T14:00:00"},
        ],
        "tasks": [
            {"status": "completed"},
            {"status": "pending"},
        ]
    }
    resp = requests.post(url, json=data, timeout=30)
    print_response(resp)
    if resp.status_code == 200:
        result = resp.json()
        if "insights" in result and "recommendations" in result:
            print_pass("返回洞察和建议")
        else:
            print_fail("缺少必要字段")
    else:
        print_fail(f"状态码: {resp.status_code}")

    # 空数据
    print_test("POST /api/v1/analyze/study-insight - 空数据")
    resp = requests.post(url, json={"sessions": [], "tasks": []}, timeout=10)
    print_response(resp)
    if resp.status_code == 200:
        print_pass("空数据返回200")
    else:
        print_fail(f"状态码: {resp.status_code}")


def main():
    parser = argparse.ArgumentParser(description="MindPulse Agent 全接口测试")
    parser.add_argument("--url", default="http://localhost:8000", help="服务地址 (默认: http://localhost:8000)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(f"\n{BOLD}测试目标: {base_url}{RESET}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查服务是否可达
    print_header("连接检查")
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.status_code == 200:
            print_pass("服务可达")
        else:
            print_fail(f"服务返回 {resp.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_fail(f"无法连接到 {base_url}")
        print(f"\n{RED}请先启动服务: uvicorn app.main:app --port 8000{RESET}")
        sys.exit(1)

    # 运行所有测试
    print_header("根路径测试")
    test_root(base_url)
    test_health(base_url)

    print_header("任务分析测试")
    test_analyze_task(base_url)

    print_header("批量分析测试")
    test_batch_analyze(base_url)

    print_header("笔记摘要测试")
    test_generate_summary(base_url)

    print_header("学习洞察测试")
    test_study_insight(base_url)

    # 打印统计
    print_header("测试统计")
    total = passed + failed
    print(f"  总计: {total} 个测试")
    print(f"  {GREEN}通过: {passed}{RESET}")
    if failed > 0:
        print(f"  {RED}失败: {failed}{RESET}")
    else:
        print(f"  失败: 0")

    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
