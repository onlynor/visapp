# 自然语言数据可视化工作台

基于 `Python + Streamlit + Plotly` 的交互式可视化应用。用户上传 `CSV / Excel` 数据后，可以直接用自然语言生成图表、查看结果摘要，并在有 OpenAI 兼容接口时启用 `LLM 驱动分析`。

## 功能

- 支持 CSV / Excel 上传
- 支持数据预览、字段识别、缺失值统计和基础清洗
- 支持柱状图、折线图、散点图、饼图、热力图
- 保留规则分析主流程，LLM 只作为可选增强层
- 支持图表 HTML 导出与汇总结果 CSV 导出
- 前台访问密码默认启用，通过 `FRONTEND_PASSWORD` 配置

## 本地运行

### uv

```bash
uv venv
uv pip install -r requirements.txt
uv run streamlit run app.py
```

### Python venv

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## 前台密码

- 默认密码通过环境变量 `FRONTEND_PASSWORD` 控制
- 未配置时默认使用 `24343`
- UI 页面不再显示默认密码提示

## Docker 部署

### 构建镜像

```bash
docker build -t vis-app .
```

### 准备配置

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 运行容器

```bash
docker run -d -p 28501:28501 --name vis-app --env-file .env vis-app
```

或者只覆盖前台密码：

```bash
docker run -d -p 28501:28501 --name vis-app -e FRONTEND_PASSWORD=your_password vis-app
```

### 访问地址

- [http://localhost:28501](http://localhost:28501)

### Docker 说明

- 容器内使用系统 Python + `pip install -r requirements.txt`
- 使用非 root 用户运行
- 已加入 `HEALTHCHECK`
- 默认监听 `28501` 端口

## LLM 驱动分析

- 仅支持 OpenAI 兼容接口
- 不支持 Anthropic 原生接口
- 支持 `/v1/chat/completions` 与 `/v1/responses`
- 不兼容 `chat.completions` 时会自动回退到 `responses`

## 文件

- [README.md](/workspace/README.md) 为项目总说明
- `docs/` 用于存放课程文档和 skill 说明
