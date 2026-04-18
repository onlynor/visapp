# ChartPlanningSkill

## Role

将自然语言指令解析为可执行的图表配置。

## Input

- 用户指令
- 当前数据列结构
- 上一轮 `ChartSpec`（可选）

## Output

- `chart_type`
- `x`
- `y`
- `agg`
- `filters`
- `title`

## Rules

- 优先选择对应数据类型的图表
- 无法确定时使用保守默认规则
- 保持输出结构化，便于 `charts.py` 消费
