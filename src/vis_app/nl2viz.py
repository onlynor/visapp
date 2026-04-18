from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

import pandas as pd


CHART_KEYWORDS = {
    "bar": ["柱状图", "条形图", "bar"],
    "line": ["折线图", "趋势图", "line"],
    "scatter": ["散点图", "相关性", "scatter"],
    "pie": ["饼图", "占比", "pie"],
    "heatmap": ["热力图", "相关矩阵", "heatmap"],
}

AGG_KEYWORDS = {
    "sum": ["总和", "合计", "汇总", "求和", "总计"],
    "mean": ["平均", "均值", "平均值"],
    "count": ["数量", "个数", "计数", "频次"],
}

SUPPORTED_CHART_TYPES = {"bar", "line", "scatter", "pie", "heatmap"}
SUPPORTED_AGG_TYPES = {"sum", "mean", "count"}


@dataclass
class ChartSpec:
    chart_type: str
    x: str | None = None
    y: str | None = None
    color: str | None = None
    agg: str = "sum"
    title: str = ""
    filters: list[dict] = field(default_factory=list)
    insight: str = ""
    rationale: str = ""


def chart_type_name(chart_type: str) -> str:
    return {
        "bar": "柱状图",
        "line": "折线图",
        "scatter": "散点图",
        "pie": "饼图",
        "heatmap": "热力图",
    }.get(chart_type, chart_type)


def _columns_by_type(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [col for col in df.columns if col not in numeric_cols]
    return numeric_cols, categorical_cols


def _find_columns(prompt: str, df: pd.DataFrame) -> list[str]:
    found: list[str] = []
    lower_prompt = prompt.lower()
    for column in df.columns:
        if column.lower() in lower_prompt or column in prompt:
            found.append(column)
    return found


def _extract_filters(prompt: str, df: pd.DataFrame) -> list[dict]:
    filters: list[dict] = []
    patterns = [
        r"筛选(?P<column>[\u4e00-\u9fa5A-Za-z0-9_]+)[为是:： ](?P<value>[\u4e00-\u9fa5A-Za-z0-9_ -]+)",
        r"仅看(?P<column>[\u4e00-\u9fa5A-Za-z0-9_]+)[为是:： ](?P<value>[\u4e00-\u9fa5A-Za-z0-9_ -]+)",
        r"只看(?P<column>[\u4e00-\u9fa5A-Za-z0-9_]+)[为是:： ](?P<value>[\u4e00-\u9fa5A-Za-z0-9_ -]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if not match:
            continue
        column = match.group("column")
        value = match.group("value").strip()
        if column in df.columns:
            filters.append({"column": column, "value": value})

    _, categorical_cols = _columns_by_type(df)
    for column in categorical_cols:
        values = df[column].dropna().astype(str).unique().tolist()
        for value in values:
            if value and value in prompt:
                exists = any(item["column"] == column and str(item["value"]) == value for item in filters)
                if not exists:
                    filters.append({"column": column, "value": value})
    return filters


def _match_chart_type(prompt: str, previous: ChartSpec | None) -> str:
    for chart_type, keywords in CHART_KEYWORDS.items():
        if any(keyword in prompt for keyword in keywords):
            return chart_type
    return previous.chart_type if previous else "bar"


def _match_agg(prompt: str, previous: ChartSpec | None) -> str:
    for agg, keywords in AGG_KEYWORDS.items():
        if any(keyword in prompt for keyword in keywords):
            return agg
    return previous.agg if previous else "sum"


def _best_categorical_axis(
    df: pd.DataFrame,
    categorical_cols: list[str],
    filters: list[dict],
    fallback: str | None = None,
) -> str | None:
    filtered_columns = {item["column"] for item in filters}
    candidates = [col for col in categorical_cols if col not in filtered_columns]
    if fallback in candidates:
        return fallback
    if candidates:
        ranked = sorted(candidates, key=lambda col: df[col].nunique(dropna=True))
        return ranked[0]
    if fallback in categorical_cols:
        return fallback
    return categorical_cols[0] if categorical_cols else None


def build_rationale(chart_type: str, x: str | None, y: str | None, agg: str) -> str:
    if chart_type == "bar":
        return f"使用柱状图对 `{x}` 分组，并对 `{y}` 执行 `{agg}` 聚合，适合类别对比。"
    if chart_type == "line":
        return f"使用折线图展示 `{x}` 与 `{y}` 的变化趋势，适合时间序列或连续趋势分析。"
    if chart_type == "scatter":
        return f"使用散点图同时编码 `{x}` 与 `{y}`，用于观察相关性、分布和异常点。"
    if chart_type == "pie":
        return f"使用饼图呈现 `{x}` 的组成结构，适合类别较少时分析占比。"
    if chart_type == "heatmap":
        return "使用热力图展示数值字段之间的相关关系，便于快速定位强弱相关特征。"
    return "根据用户意图选择了合适的图表。"


def build_placeholder_insight(
    chart_type: str,
    x: str | None,
    y: str | None,
    filters: list[dict],
) -> str:
    pieces = [f"当前图表类型为{chart_type_name(chart_type)}。"]
    if x:
        pieces.append(f"核心分析维度是 `{x}`。")
    if y:
        pieces.append(f"主要度量字段是 `{y}`。")
    if filters:
        text = "、".join(f"{item['column']}={item['value']}" for item in filters)
        pieces.append(f"已应用筛选条件：{text}。")
    pieces.append("可继续输入“改成折线图”“只看某地区”“按某字段着色”等指令进行迭代。")
    return "".join(pieces)


def normalize_chart_spec(spec: ChartSpec, df: pd.DataFrame, previous: ChartSpec | None = None) -> ChartSpec:
    numeric_cols, categorical_cols = _columns_by_type(df)

    if spec.chart_type not in SUPPORTED_CHART_TYPES:
        spec.chart_type = previous.chart_type if previous else "bar"
    if spec.agg not in SUPPORTED_AGG_TYPES:
        spec.agg = previous.agg if previous else "sum"

    if spec.chart_type == "scatter":
        numeric_refs = [col for col in [spec.x, spec.y] if col in numeric_cols]
        if len(numeric_refs) >= 2:
            spec.x, spec.y = numeric_refs[0], numeric_refs[1]
        elif len(numeric_cols) >= 2:
            spec.x, spec.y = numeric_cols[0], numeric_cols[1]
    elif spec.chart_type == "heatmap":
        spec.x, spec.y = None, None
    else:
        if spec.x not in df.columns:
            spec.x = previous.x if previous and previous.x in df.columns else None
        if spec.y not in df.columns:
            spec.y = previous.y if previous and previous.y in df.columns else None

        if spec.chart_type == "pie":
            spec.x = _best_categorical_axis(df, categorical_cols, spec.filters, fallback=spec.x)
            if spec.y is None and numeric_cols:
                spec.y = numeric_cols[0]
        else:
            if spec.x is None or spec.x in numeric_cols:
                spec.x = _best_categorical_axis(
                    df,
                    categorical_cols,
                    spec.filters,
                    fallback=previous.x if previous else spec.x,
                ) or (df.columns[0] if len(df.columns) else None)
            if spec.y is None and numeric_cols:
                spec.y = numeric_cols[0]

    if spec.color not in df.columns:
        spec.color = previous.color if previous and previous.color in df.columns else None

    valid_filters: list[dict] = []
    for item in spec.filters:
        column = item.get("column")
        value = item.get("value")
        if column in df.columns and value not in (None, ""):
            valid_filters.append({"column": column, "value": str(value)})
    spec.filters = valid_filters

    if not spec.title:
        spec.title = f"{chart_type_name(spec.chart_type)}: {spec.x or '字段分析'}"
        if spec.y:
            spec.title = f"{spec.title} 与 {spec.y}"
    if not spec.rationale:
        spec.rationale = build_rationale(spec.chart_type, spec.x, spec.y, spec.agg)
    if not spec.insight:
        spec.insight = build_placeholder_insight(spec.chart_type, spec.x, spec.y, spec.filters)

    return spec


def chart_spec_from_dict(data: dict[str, Any], df: pd.DataFrame, previous: ChartSpec | None = None) -> ChartSpec:
    spec = ChartSpec(
        chart_type=str(data.get("chart_type", previous.chart_type if previous else "bar")),
        x=data.get("x"),
        y=data.get("y"),
        color=data.get("color"),
        agg=str(data.get("agg", previous.agg if previous else "sum")),
        title=str(data.get("title", "")),
        filters=list(data.get("filters", [])),
        insight=str(data.get("insight", "")),
        rationale=str(data.get("rationale", "")),
    )
    return normalize_chart_spec(spec, df, previous=previous)


def infer_chart_spec(prompt: str, df: pd.DataFrame, previous: ChartSpec | None = None) -> ChartSpec:
    prompt = prompt.strip()
    numeric_cols, categorical_cols = _columns_by_type(df)
    referenced_columns = _find_columns(prompt, df)
    chart_type = _match_chart_type(prompt, previous)
    agg = _match_agg(prompt, previous)
    filters = _extract_filters(prompt, df)

    x = previous.x if previous else None
    y = previous.y if previous else None

    if chart_type == "scatter":
        numeric_refs = [col for col in referenced_columns if col in numeric_cols]
        if len(numeric_refs) >= 2:
            x, y = numeric_refs[0], numeric_refs[1]
        elif len(numeric_cols) >= 2:
            x, y = numeric_cols[0], numeric_cols[1]
    elif chart_type == "heatmap":
        x, y = None, None
    else:
        categorical_refs = [col for col in referenced_columns if col in categorical_cols]
        numeric_refs = [col for col in referenced_columns if col in numeric_cols]
        if categorical_refs:
            x = categorical_refs[0]
        if numeric_refs:
            y = numeric_refs[0]
        if chart_type == "pie":
            x = _best_categorical_axis(df, categorical_cols, filters, fallback=x)
        elif x is None:
            x = categorical_cols[0] if categorical_cols else df.columns[0]
        if y is None and numeric_cols:
            y = numeric_cols[0]

    color = previous.color if previous and previous.color in df.columns else None
    if "按" in prompt and "着色" in prompt:
        for column in df.columns:
            if column in prompt:
                color = column
                break

    spec = ChartSpec(
        chart_type=chart_type,
        x=x,
        y=y,
        color=color,
        agg=agg,
        title="",
        filters=filters,
        insight="",
        rationale="",
    )
    return normalize_chart_spec(spec, df, previous=previous)
