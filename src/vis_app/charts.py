from __future__ import annotations

import pandas as pd

from vis_app.data_utils import filter_dataframe
from vis_app.nl2viz import ChartSpec, chart_type_name


def _aggregate(df: pd.DataFrame, x: str, y: str, agg: str) -> pd.DataFrame:
    if agg == "count":
        return df.groupby(x, dropna=False).size().reset_index(name="计数")
    agg_name = {"sum": "总和", "mean": "平均值"}.get(agg, agg)
    return df.groupby(x, dropna=False, as_index=False)[y].agg(agg).rename(columns={y: agg_name})


def build_figure(df: pd.DataFrame, spec: ChartSpec):
    import plotly.express as px

    filtered = filter_dataframe(df, spec.filters)

    if filtered.empty:
        raise ValueError("筛选后没有可展示的数据，请调整条件后重试。")

    if spec.chart_type == "heatmap":
        numeric = filtered.select_dtypes(include="number")
        if numeric.shape[1] < 2:
            raise ValueError("热力图至少需要两个数值字段。")
        corr = numeric.corr(numeric_only=True)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="Teal",
            aspect="auto",
            title="数值字段相关性热力图",
        )
        return fig, filtered, corr.reset_index()

    if spec.chart_type == "scatter":
        if not spec.x or not spec.y:
            raise ValueError("散点图需要两个数值字段。")
        fig = px.scatter(
            filtered,
            x=spec.x,
            y=spec.y,
            color=spec.color,
            title=spec.title,
            template="plotly_white",
        )
        fig.update_traces(marker={"size": 10, "opacity": 0.78})
        return fig, filtered, filtered[[spec.x, spec.y]].describe().reset_index()

    if not spec.x or not spec.y:
        raise ValueError(f"{chart_type_name(spec.chart_type)} 需要一个分类字段和一个数值字段。")

    if spec.chart_type == "pie":
        numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
        categorical_cols = [col for col in filtered.columns if col not in numeric_cols]
        if spec.x not in filtered.columns or spec.x not in categorical_cols:
            available = [col for col in categorical_cols if col != spec.y]
            if not available:
                raise ValueError("当前数据不足以生成饼图，请换一种图表类型。")
            spec.x = available[0]

    grouped = _aggregate(filtered, spec.x, spec.y, spec.agg)
    value_column = grouped.columns[-1]

    if spec.chart_type == "bar":
        fig = px.bar(
            grouped,
            x=spec.x,
            y=value_column,
            color=spec.x if grouped[spec.x].nunique() <= 12 else None,
            title=spec.title,
            template="plotly_white",
            text_auto=True,
        )
    elif spec.chart_type == "line":
        fig = px.line(
            grouped.sort_values(spec.x),
            x=spec.x,
            y=value_column,
            markers=True,
            title=spec.title,
            template="plotly_white",
        )
    elif spec.chart_type == "pie":
        if spec.x not in grouped.columns:
            fallback_names = [col for col in grouped.columns if col != value_column]
            if not fallback_names:
                raise ValueError("当前图表缺少分类字段，无法生成饼图。")
            spec.x = fallback_names[0]
        top_grouped = grouped.sort_values(value_column, ascending=False).head(8)
        fig = px.pie(
            top_grouped,
            names=spec.x,
            values=value_column,
            title=spec.title,
            hole=0.38,
        )
    else:
        raise ValueError(f"暂不支持图表类型：{spec.chart_type}")

    fig.update_layout(
        margin={"l": 24, "r": 24, "t": 60, "b": 24},
        legend_title_text="",
        paper_bgcolor="#f6f6f1",
        plot_bgcolor="#ffffff",
        font={"family": "Microsoft YaHei, Segoe UI, sans-serif"},
    )

    if spec.chart_type in {"bar", "line"}:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#d9e1dd")

    return fig, filtered, grouped


def figure_to_html(fig) -> str:
    return fig.to_html(include_plotlyjs="cdn", full_html=True)
