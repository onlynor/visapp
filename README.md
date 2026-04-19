# 自然语言数据可视化工作台

基于 `Python + Streamlit + Plotly` 的交互式数据可视化工作台。默认使用规则分析流程，可选接入 OpenAI 兼容 LLM 做增强解析，失败时自动回退到规则路径。

- 演示站点: https://visapp.streamlit.app/
- 默认密码: 24343
## 功能

- CSV / Excel 上传与预览
- 轻量数据清洗（缺失值填补、去重、IQR 截尾）
- 自然语言生成柱状图、折线图、散点图、饼图、热力图
- 多轮指令迭代
- 图表 HTML 导出与 CSV 汇总导出
- OpenAI 兼容接口接入（可选）

## 项目结构

```text
.
|-- app.py
|-- src/vis_app/
|   |-- app.py
|   |-- charts.py
|   |-- data_utils.py
|   |-- llm.py
|   `-- nl2viz.py
|-- data/
|-- assets/images/
|-- docs/
|-- .env.example
|-- Dockerfile
|-- pyproject.toml
|-- requirements.txt
`-- uv.lock
```

## 环境要求

- Python 3.11+
- `uv` 或普通 `venv`

## 启动

### 方式 1：`uv`

```powershell
uv venv
.\.venv\Scripts\activate
uv pip install -r requirements.txt
uv run streamlit run app.py
```

### 方式 2：`venv`

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## 配置

复制 `.env.example` 为 `.env`：

```powershell
cp .env.example .env
```

支持的环境变量：

- `FRONTEND_PASSWORD`：前台访问密码(默认: 24343)
- `OPENAI_API_KEY`：LLM API Key
- `OPENAI_BASE_URL`：OpenAI 兼容 API 根地址
- `OPENAI_MODEL`：模型名称

LLM 接入约束：

- 只支持 OpenAI 兼容接口，不支持 Anthropic 原生接口
- 优先调用 `/v1/chat/completions`，必要时自动尝试 `/v1/responses`
- `Base URL` 需填写 API 根地址，不要填写网站首页

## Docker

构建镜像：

```powershell
docker build -t vis-studio .
```

运行容器：

```powershell
docker run --rm -p 28501:28501 --env-file .env vis-studio
```

默认端口为 `28501`。

## 开发说明

- 项目优先使用 `uv` 管理环境与依赖
- 为兼容普通 Python 环境，仍保留 `requirements.txt`
- `.env` 不提交，`.env.example` 保留在仓库

## 文档

- [架构说明](docs/skill_design.md)
- [Dataset Understanding Skill](docs/skills/dataset_understanding_skill.md)
- [Cleaning Preparation Skill](docs/skills/cleaning_preparation_skill.md)
- [Chart Planning Skill](docs/skills/chart_planning_skill.md)
- [Insight Explanation Skill](docs/skills/insight_explanation_skill.md)
- [Iteration Refinement Skill](docs/skills/iteration_refinement_skill.md)
