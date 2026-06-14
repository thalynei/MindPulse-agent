#!/bin/bash
# 运行测试脚本

set -e

echo "🧪 运行测试..."

# 激活虚拟环境
source .venv/bin/activate 2>/dev/null || .venv/Scripts/activate 2>/dev/null || true

# 运行单元测试
echo "📦 运行单元测试..."
pytest tests/unit -v --tb=short

# 运行集成测试
echo "🔗 运行集成测试..."
pytest tests/integration -v --tb=short

# 生成覆盖率报告
echo "📊 生成覆盖率报告..."
pytest --cov=app --cov-report=html --cov-report=term

echo "✅ 测试完成！"
