.PHONY: help install dev test lint format run clean

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -r requirements.txt

dev: ## 安装开发依赖
	pip install -r requirements.txt
	pip install black isort flake8 mypy pytest pytest-cov

test: ## 运行测试
	pytest

test-unit: ## 运行单元测试
	pytest tests/unit -v

test-integration: ## 运行集成测试
	pytest tests/integration -v

test-cov: ## 运行测试并生成覆盖率报告
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## 运行代码检查
	flake8 app/ tests/
	mypy app/

format: ## 格式化代码
	black app/ tests/
	isort app/ tests/

run: ## 启动服务
	uvicorn app.main:app --reload --port 8000

run-prod: ## 以生产模式启动服务
	uvicorn app.main:app --host 0.0.0.0 --port 8000

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage

docker-build: ## 构建 Docker 镜像
	docker-compose build

docker-up: ## 启动 Docker 服务
	docker-compose up -d

docker-down: ## 停止 Docker 服务
	docker-compose down
