# Skill Design

## Overview

项目将可视化流程拆成五个能力块：

1. 数据理解
2. 清洗与准备
3. 图表规划
4. 结果解读
5. 迭代修改

## Runtime Path

- 默认路径：规则解析
- 增强路径：OpenAI 兼容 LLM
- 回退策略：LLM 不可用或返回异常时，直接回退到规则路径

## Core Mapping

- `src/vis_app/data_utils.py`：数据读取、预处理、轻量清洗
- `src/vis_app/nl2viz.py`：规则解析，将自然语言指令映射为 `ChartSpec`
- `src/vis_app/charts.py`：按 `ChartSpec` 生成 Plotly 图表与汇总结果
- `src/vis_app/llm.py`：LLM 接入、连接检测、结构化输出
- `src/vis_app/app.py`：Streamlit UI 、状态管理、交互流程

## Boundary

- UI 层只处理输入、状态和反馈
- 图表逻辑放在 `nl2viz.py` 与 `charts.py`
- LLM 是可选增强层，不影响默认可用路径
