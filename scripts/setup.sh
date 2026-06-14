#!/bin/bash
# MindPulse Agent 开发环境设置脚本

set -e

echo "🚀 设置 MindPulse Agent 开发环境..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate || .venv/Scripts/activate

# 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置您的环境变量"
fi

echo "✅ 开发环境设置完成！"
echo ""
echo "常用命令："
echo "  启动服务: uvicorn app.main:app --reload --port 8000"
echo "  运行测试: pytest"
echo "  代码检查: flake8 app/ tests/"
echo "  类型检查: mypy app/"
