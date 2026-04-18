# 可视化 Skill 设计总览

## 设计目标

本项目的自然语言可视化能力不是单一步骤，而是一个可拆分、可组合、可回退的工作流。整体设计围绕以下目标展开：

- 支持从数据理解到图表生成再到结果解读的完整链路
- 在无 API 条件下也能稳定运行
- 在接入 OpenAI 兼容接口后提供更强的语义理解与分析补充
- 保持规则分析为主干，LLM 作为可选增强层
- 出现失败时自动回退，不影响主流程可用性

## 能力拆分

项目把可视化过程拆成 5 个相互衔接的 Skill：

1. `DatasetUnderstandingSkill`
2. `CleaningPreparationSkill`
3. `ChartPlanningSkill`
4. `InsightExplanationSkill`
5. `IterationRefinementSkill`

这样的拆分方式有两个好处：
- 每一段职责清晰，便于单独优化
- 既适合课程作业说明，也适合后续工程扩展

## 工作流映射

### 1. 数据理解

目标：识别字段结构与数据约束。

主要任务：
- 区分数值字段、类别字段、时间字段
- 识别缺失值、重复值和异常值
- 为后续自然语言解析提供字段候选上下文

对应实现：
- `src/vis_app/data_utils.py`

### 2. 数据清洗准备

目标：在不破坏原始数据的前提下，完成可视化前的轻量处理。

主要任务：
- 处理缺失值
- 去除重复记录
- 做基础类型修正
- 输出清洗记录，便于用户理解处理过程

对应实现：
- `src/vis_app/data_utils.py`

### 3. 图表规划

目标：把自然语言指令转换为结构化图表配置。

主要任务：
- 判断图表类型
- 匹配字段
- 推断聚合方式
- 解析筛选条件
- 在配置不合理时给出自动修正

对应实现：
- `src/vis_app/nl2viz.py`
- `src/vis_app/charts.py`

## 4. 结果解读

目标：输出面向用户的简明分析说明。

主要任务：
- 解释为什么选择该图表
- 说明关注的核心字段
- 给出基础结论和下一步建议

对应实现：
- 规则解读：`src/vis_app/nl2viz.py`
- LLM 补充分析：`src/vis_app/llm.py`

## 5. 多轮迭代

目标：支持在上一轮图表基础上继续修改。

主要任务：
- 识别“改成折线图”“只看家电”“按地区筛选”等增量指令
- 复用上一轮图表上下文
- 保留历史记录，支持连续操作

对应实现：
- `src/vis_app/app.py`
- `src/vis_app/nl2viz.py`

## 输入输出约束

自然语言分析阶段最终会得到结构化 `ChartSpec`，核心字段包括：

- `chart_type`
- `x`
- `y`
- `agg`
- `color`
- `filters`
- `title`

这让规则流程与 LLM 流程都能汇聚到同一套图表渲染逻辑上，减少重复实现。

## LLM 增强策略

项目没有把 LLM 当作唯一入口，而是采用“规则优先，可选增强，失败回退”的方式：

- 默认使用规则分析完成自然语言转图表配置
- 用户填写 OpenAI 兼容接口后，可以启用 `LLM 驱动分析`
- 若兼容网关不支持 `/v1/chat/completions`，自动尝试 `/v1/responses`
- 若仍失败，则回退到规则分析路径

这样能兼顾稳定性、速度和用户体验。

## 文档拆分说明

本总览用于说明整体设计，详细拆分文档放在：

- `docs/skills/dataset_understanding_skill.md`
- `docs/skills/cleaning_preparation_skill.md`
- `docs/skills/chart_planning_skill.md`
- `docs/skills/insight_explanation_skill.md`
- `docs/skills/iteration_refinement_skill.md`