# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

MindPulse Agent 是 MindPulse 系统的 AI 核心模块，作为独立微服务为 Java 后端提供自然语言分析能力。

**职责边界：** 只开发 Agent 模块，前端和后端禁止开发。

## 技术栈

| 组件 | 说明 |
|------|------|
| Python | 3.10+ |
| Web 框架 | FastAPI + Uvicorn |
| AI 引擎 | Ollama (qwen2.5:1.5b) |
| 日期解析 | dateparser |
| HTTP 客户端 | aiohttp |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Ollama 服务
ollama run qwen2.5:1.5b

# 启动 Agent 服务
uvicorn app.main:app --reload --port 8000

# 测试接口
curl -X POST http://localhost:8000/api/v1/analyze/task \
  -H "Content-Type: application/json" \
  -d '{"task_description": "明天下午3点前交数学作业"}'
```

## 项目结构

```
MindPulse-agent/
├── app/
│   ├── main.py                    # FastAPI 入口
│   ├── core/
│   │   ├── config.py              # 全局配置
│   │   └── ollama_client.py       # Ollama HTTP 客户端（连接池复用）
│   ├── api/v1/endpoints/
│   │   ├── tasks.py               # 任务分析端点
│   │   ├── notes.py               # 笔记摘要端点
│   │   └── study_insight.py       # 学习洞察端点
│   ├── agents/
│   │   ├── task_analyzer.py       # 任务分析智能体
│   │   ├── note_summarizer.py     # 笔记摘要智能体
│   │   └── study_insight_agent.py # 学习洞察智能体
│   └── utils/
│       ├── task_parser.py         # 任务规则解析器
│       ├── note_parser.py         # 笔记规则解析器
│       └── study_insight_parser.py # 学习洞察规则解析器
├── tests/                         # 测试目录
├── requirements.txt               # 生产依赖
├── requirements-dev.txt           # 开发依赖
├── Dockerfile                     # 多阶段构建
└── docker-compose.yml             # 容器编排
```

## 核心架构

### 任务分析流程

```
请求 → FastAPI → TaskAnalyzerAgent → Ollama (成功) → 返回结构化 JSON
                                    ↓ (失败)
                              规则解析器 → 返回结构化 JSON
```

### 规则解析降级

当 Ollama 不可用或返回无效 JSON 时，使用 `task_parser.py` 进行规则解析：

| 维度 | 实现方式 |
|------|----------|
| 日期 | dateparser + 正则匹配 (今天/明天/下周等) |
| 优先级 | 关键词匹配 (紧急→high, 有空→low, 默认→medium) |
| 分类 | 关键词匹配 (作业→homework, 考试→exam) |
| 标签 | 学科关键词映射 (数学→math, 物理→physics) |

## API 接口

### 任务分析

```
POST /api/v1/analyze/task
```

**请求：**
```json
{"task_description": "明天下午3点前完成数学作业"}
```

**响应：**
```json
{
  "original_description": "明天下午3点前完成数学作业",
  "analyzed_task": {
    "title": "完成数学作业",
    "due_date": "2026-05-30T15:00:00",
    "priority": "high",
    "category": "homework",
    "tags": ["math"]
  }
}
```

### 批量分析

```
POST /api/v1/analyze/batch-analyze
```

**请求：** `["明天交数学作业", "下周三期中考试"]`

**响应：** `{"results": [{"original_description": "...", "analyzed_task": {...}}, ...]}`

### 笔记摘要

```
POST /api/v1/analyze/generate_summary
```

**请求：**
```json
{"note_content": "# 量子力学\n波粒二象性是量子力学的基础。"}
```

**响应：**
```json
{
  "title": "量子力学",
  "summary": "本文介绍了量子力学的基础概念，包括波粒二象性。",
  "tags": "physics"
}
```

## 配置项

定义在 `app/core/config.py`，通过环境变量注入：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 8000 | 服务端口 |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama 地址 |
| `OLLAMA_MODEL` | qwen2.5:1.5b | 模型名称 |
| `OLLAMA_ENABLED` | true | 是否启用 Ollama |

## 开发规范

### AI 模型调用
- 使用共享的 `OllamaClient`（`app/core/ollama_client.py`），连接池复用
- 使用 Ollama `format: "json"` 强制结构化输出
- temperature 设为 0.1，seed 设为 42，保证输出稳定性
- 启动时预检 Ollama 可用性，缓存结果避免无效等待

### 异常处理
- Ollama 调用失败 → 降级到规则解析，不抛异常
- 规则解析兜底保证返回完整字段（title 至少为原始描述）
- 日志记录降级事件

### 接口设计
- 所有端点使用 Pydantic 模型做请求/响应校验
- 错误统一抛 `HTTPException`，status_code 明确
- 响应格式保持一致，不随意增减字段

## 常用命令

```bash
# 运行测试
pytest                      # 全部测试
pytest tests/unit           # 单元测试
pytest tests/integration    # 集成测试
pytest --cov=app            # 覆盖率报告

# 代码检查
make lint                   # 运行 flake8 + mypy
make format                 # black + isort 格式化

# Docker
docker-compose up -d
```

## 已完成功能

| 功能 | 接口 | 状态 |
|------|------|------|
| 任务分析 | `POST /api/v1/analyze/task` | ✅ |
| 批量分析 | `POST /api/v1/analyze/batch-analyze` | ✅ |
| 笔记摘要 | `POST /api/v1/analyze/generate_summary` | ✅ |
| 学习洞察 | `POST /api/v1/analyze/study-insight` | ✅ |
| 健康检查 | `GET /health` | ✅ |

## 待开发任务

| 优先级 | 任务 | 状态 |
|--------|------|------|
| P1 | 批量分析集成到 Java 后端 | 待开发 |

## 语言规范

- 默认使用中文回复
