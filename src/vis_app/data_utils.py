from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


@dataclass
class DataProfile:
    rows: int
    columns: int
    dtypes: pd.DataFrame
    missing: pd.DataFrame
    numeric_summary: pd.DataFrame


@st.cache_data(show_spinner=False)
def _load_csv_bytes(content: bytes) -> pd.DataFrame:
    return pd.read_csv(BytesIO(content))


@st.cache_data(show_spinner=False)
def _load_excel_bytes(content: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(content))


def load_dataset(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        raise ValueError("未上传文件。")

    file_name = uploaded_file.name.lower()
    content = uploaded_file.getvalue()

    if file_name.endswith(".csv"):
        return _load_csv_bytes(content)
    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return _load_excel_bytes(content)
    raise ValueError("仅支持 CSV 或 Excel 文件。")


@st.cache_data(show_spinner=False)
def load_sample_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def profile_dataset(df: pd.DataFrame) -> DataProfile:
    dtypes = pd.DataFrame({"字段": df.columns, "类型": [str(dtype) for dtype in df.dtypes]}).reset_index(drop=True)
    missing = pd.DataFrame(
        {
            "字段": df.columns,
            "缺失值数量": df.isna().sum().values,
            "缺失率(%)": (df.isna().mean().round(4) * 100).values,
        }
    ).reset_index(drop=True)

    numeric_summary = df.select_dtypes(include=np.number).describe().T.reset_index()
    if not numeric_summary.empty:
        numeric_summary = numeric_summary.rename(columns={"index": "字段"})

    return DataProfile(
        rows=df.shape[0],
        columns=df.shape[1],
        dtypes=dtypes,
        missing=missing,
        numeric_summary=numeric_summary,
    )


@st.cache_data(show_spinner=False)
def clean_dataset(
    df: pd.DataFrame,
    missing_strategy: str = "median_mode",
    drop_duplicates: bool = True,
    outlier_strategy: str = "clip_iqr",
) -> tuple[pd.DataFrame, list[str]]:
    cleaned = df.copy()
    notes: list[str] = []

    if drop_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        removed = before - len(cleaned)
        if removed:
            notes.append(f"移除了 {removed} 条重复记录。")

    for column in cleaned.columns:
        series = cleaned[column]
        if series.isna().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(series):
            fill_value = series.median() if missing_strategy == "median_mode" else series.mean()
        else:
            mode = series.mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "未知"
        cleaned[column] = series.fillna(fill_value)
        notes.append(f"字段 `{column}` 已完成缺失值填补。")

    if outlier_strategy == "clip_iqr":
        for column in cleaned.select_dtypes(include=np.number).columns:
            q1 = cleaned[column].quantile(0.25)
            q3 = cleaned[column].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0 or pd.isna(iqr):
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outside = ((cleaned[column] < lower) | (cleaned[column] > upper)).sum()
            if outside:
                cleaned[column] = cleaned[column].clip(lower=lower, upper=upper)
                notes.append(f"字段 `{column}` 使用 IQR 方法处理了 {outside} 个异常值。")

    return cleaned, notes


def filter_dataframe(df: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    filtered = df.copy()
    for item in filters:
        column = item["column"]
        value = item["value"]
        if column not in filtered.columns:
            continue
        filtered = filtered[filtered[column].astype(str) == str(value)]
    return filtered
