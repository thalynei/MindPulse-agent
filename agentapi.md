# MindPulse Agent 模块接口文档

> Agent 服务基地址：`http://localhost:8000/api/v1/analyze`（默认，可通过环境变量 `AI_SERVICE_URL` 覆盖）
> Java 后端通过 `AiAgentClient` 调用以下接口，路由前缀为 `/api/v1/analyze`

---

## 一、Python Agent 直接暴露的接口

> FastAPI 服务，端口 8000，路由前缀 `/api/v1/analyze`

### 1. 单条任务分析

```
POST /api/v1/analyze/task
```

**请求体：**
```json
{
  "task_description": "明天下午3点前完成数学作业"
}
```

**响应体：**
```json
{
  "original_description": "明天下午3点前完成数学作业",
  "analyzed_task": {
    "title": "完成数学作业",
    "due_date": "2026-05-29T15:00:00",
    "priority": "high",
    "category": "homework",
    "estimated_duration": null,
    "tags": ["math"]
  }
}
```

**analyzed_task 字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 任务标题（从描述中提取，去除时间信息） |
| due_date | string \| null | 截止日期，ISO 8601 格式，无法确定时为 null |
| priority | string | 优先级：`low` / `medium` / `high` / `urgent` |
| category | string | 分类：`homework` / `exam` / `project` / `review` / `general` |
| estimated_duration | int \| null | 预估完成时间（分钟），无法确定时为 null |
| tags | string[] | 标签列表（学科等） |

**错误响应（500）：**
```json
{
  "detail": "任务分析失败: {错误信息}"
}
```

---

### 2. 批量任务分析

```
POST /api/v1/analyze/batch-analyze
```

**请求体：**
```json
["明天交数学作业", "下周三期中考试", "有空复习英语"]
```

**响应体：**
```json
{
  "results": [
    {
      "original_description": "明天交数学作业",
      "analyzed_task": { ... }
    },
    {
      "original_description": "下周三期中考试",
      "analyzed_task": { ... }
    }
  ]
}
```

---

## 二、Java 后端调用 Agent 的接口（AiAgentClient）

> Java 后端通过 `RestTemplate` 调用 Agent 服务，配置项：`ai.service.base-url`（默认 `http://localhost:8000/api/v1/analyze`）

### 1. 任务解析

```
POST {ai.service.base-url}/task
```

**请求体：**
```json
{
  "task_description": "明天下午3点前完成数学作业"
}
```

**期望响应体：**
```json
{
  "title": "完成数学作业",
  "description": "",
  "due_date": "2026-05-29T15:00:00",
  "priority": "high",
  "category": "homework"
}
```

**超时配置：** 连接超时 5s，读取超时 15s，最大重试 2 次

**降级策略：** 调用失败时返回 fallback：
```json
{
  "title": "原始描述（截取前50字）",
  "description": "原始描述全文",
  "due_date": "",
  "priority": "medium",
  "category": ""
}
```

---

### 2. 笔记摘要生成

```
POST {ai.service.base-url}/generate_summary
```

**请求体：**
```json
{
  "note_content": "今天的课程内容是关于量子力学的基本原理..."
}
```

**期望响应体：**
```json
{
  "title": "量子力学基本原理笔记",
  "summary": "本文介绍了量子力学的基本概念，包括波粒二象性、不确定性原理等核心内容。",
  "tags": "physics,quantum"
}
```

**降级策略：** 调用失败时返回 fallback：
```json
{
  "title": "Auto-generated Title",
  "summary": "Could not generate summary due to AI service error",
  "tags": ""
}
```

---

## 三、Java 后端涉及 Agent 的业务接口

### 1. AI 任务解析（含语义缓存）

```
POST /api/tasks/parse
Authorization: Bearer <JWT>
Content-Type: application/json
```

**请求体：**
```json
{
  "taskDescription": "明天下午3点前完成数学作业"
}
```

**处理流程：**
1. `SemanticCacheService.normalize()` 归一化文本
2. SHA-256 哈希 → Redis 查缓存
3. 缓存命中 → 直接返回（~45ms）
4. 缓存未命中 → 调用 `AiAgentClient.parseTask()` → `TaskValidationService` 校验 → 写缓存 → 入库（~980ms）

**响应体（ApiResponse<TaskParseResponse>）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "parsedTask": {
      "title": "完成数学作业",
      "dueDate": "2026-05-29T15:00:00",
      "priority": "high",
      "category": "homework"
    },
    "createdTask": { ... },
    "fromCache": false,
    "responseTimeMs": 980
  }
}
```

---

### 2. 笔记摘要（同步，已废弃）

```
POST /api/notes/{id}/summary
Authorization: Bearer <JWT>
```

直接调用 `AiAgentClient.generateSummary()`，同步等待返回。**建议使用异步接口替代。**

---

### 3. 笔记异步上传（推荐）

```
POST /api/notes/async
Authorization: Bearer <JWT>
Content-Type: multipart/form-data
```

**处理流程：**
1. 保存笔记到数据库（status=processing），立即返回
2. `NoteSummaryProducer` 投递消息到 RabbitMQ（exchange: `note.summary.exchange`，routing key: `note.summary`）
3. `NoteSummaryConsumer` 异步消费，调用 `AiAgentClient.generateSummary()`
4. 更新数据库摘要/标签
5. WebSocket 推送结果到 `/user/{username}/queue/note-summary`

---

### 4. 语义缓存统计

```
GET /api/tasks/cache-stats
Authorization: Bearer <JWT>
```

**响应体：**
```json
{
  "code": 200,
  "data": {
    "totalRequests": 120,
    "cacheHits": 85,
    "cacheMisses": 35,
    "hitRate": "70.83%"
  }
}
```

---

## 四、接口路由对照表

| 功能 | Python Agent 路径 | Java 后端调用路径 | 说明 |
|------|-------------------|-------------------|------|
| 任务分析 | `POST /api/v1/analyze/task` | `POST /api/v1/analyze/task` | 已对齐 |
| 笔记摘要 | `POST /api/v1/analyze/generate_summary` | `POST /api/v1/analyze/generate_summary` | 已对齐 |
| 批量分析 | `POST /api/v1/analyze/batch-analyze` | （未调用） | Agent 端已有，后端未集成 |
| 学习洞察 | `POST /api/v1/analyze/study-insight` | （未调用） | Agent 端已有，后端未集成 |

> Java 后端 `AiAgentClient` 调用路径已对齐到 `/api/v1/analyze` 前缀。

---

## 五、AI 支撑服务

### SemanticCacheService（语义缓存）

- 文本归一化：小写 + 去标点 + 同义词替换
- SHA-256 哈希生成缓存 key，前缀 `task:cache:`
- Redis 存储，TTL 24 小时
- 统计命中率、总请求数

### TaskValidationService（任务校验）

- title：非空，长度 ≤ 200
- priority：必须为 `high` / `medium` / `low` 之一
- due_date：ISO 8601 格式校验
- category：逗号分隔的标签字符串

---

## 六、技术栈

| 组件 | 说明 |
|------|------|
| Python Agent | FastAPI + Ollama (qwen2.5:1.5b) |
| Ollama | 本地 LLM 推理，端口 11434 |
| Java 后端 | Spring Boot 3.1.5 + RestTemplate |
| 消息队列 | RabbitMQ（笔记摘要异步链路） |
| 缓存 | Redis（语义缓存） |
| 实时推送 | WebSocket STOMP |
