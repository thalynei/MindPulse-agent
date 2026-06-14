#!/bin/bash
# 代码检查脚本

set -e

echo "🔍 运行代码检查..."

# 激活虚拟环境
source .venv/bin/activate 2>/dev/null || .venv/Scripts/activate 2>/dev/null || true

# 运行 flake8
echo "📦 运行 flake8..."
flake8 app/ tests/ --max-line-length=100 --ignore=E501,W503

# 运行 mypy
echo "🔧 运行 mypy..."
mypy app/ --ignore-missing-imports

# 运行 black 检查
echo "🎨 检查代码格式..."
black --check app/ tests/

# 运行 isort 检查
echo "📚 检查导入排序..."
isort --check-only app/ tests/

echo "✅ 代码检查完成！"
