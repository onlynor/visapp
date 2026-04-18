# IterationRefinementSkill

## Role

处理基于上一轮结果的追加指令，保持迭代上下文。

## Input

- 本轮用户指令
- 上一轮 `ChartSpec`
- 当前数据集

## Output

- 更新后的 `ChartSpec`
- 当前迭代摘要
- 历史记录

## Rules

- 能局部修改时不重建整个意图
- 新指令与上一轮冲突时以新指令为准
- 历史记录需可回看
