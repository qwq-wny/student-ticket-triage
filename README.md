# 客服工单优先级分类系统

这是一个简单的机器学习项目。API 会读取一条客服工单，并预测它的优先级："urgent"、"high"、"normal" 或 "low"。

模型使用 scikit-learn 的逻辑回归，训练特征包括：

- 工单文本
- 客户等级
- 每月收入

数据是合成数据，不包含任何真实客户隐私信息。

## 本地运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

启动后打开：

<http://127.0.0.1:8000/docs>

示例请求：

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"production is down\",\"customer_tier\":\"premium\",\"monthly_revenue\":1000}"
```

## 测试和代码检查

```bash
ruff format --check .
ruff check .
pytest
```

## 数据和训练

项目使用 DVC 管理两个小数据集版本：

- "data/tickets_v1.csv.dvc"：150 条数据，类别不均衡，包含少量噪声标签
- "data/tickets_v2.csv.dvc"：240 条数据，类别均衡，并做了清洗和增强

原始 CSV 文件不会提交到 Git。如果已经配置 Azure DVC 存储，可以执行：

```bash
dvc pull
```

也可以重新生成本地测试数据：

```bash
python ml/scripts/build_dataset.py v1
python ml/scripts/build_dataset.py v2
```

训练两个 MLflow 实验：

```bash
pip install -r requirements-ml.txt
python -m ml.train --config ml/configs/baseline.json
python -m ml.train --config ml/configs/improved.json
```

MLflow 运行记录会写入 "ml/mlruns"。两次实验的指标说明见 "ml/README_experiments.md"。

## Git 和 CI/CD 流程

分支路径：

```text
feature/* -> dev -> staging -> main
```

GitHub Actions 会执行：

- 向"dev"、"staging" 或 "main" 提 PR：格式检查、Ruff、测试、Docker 镜像构建
- 推送到 "staging"：使用 staging 环境的 secrets 生成 ".env"，并构建 staging 镜像
- 推送到 "main"：使用 production 环境的 secrets 生成 ".env"，并构建 production 镜像

这个项目不做真正的外部部署，只构建不同环境的镜像。

## Docker 说明

本机不运行 Docker Desktop。Docker 镜像由 GitHub Actions 在云端构建和验证。

如果你自己的电脑上有 Docker，也可以手动构建：

```bash
docker build -t ticket-triage .
docker run --rm -p 8000:8000 ticket-triage
```

CI 状态：由 GitHub Actions 自动检查。
