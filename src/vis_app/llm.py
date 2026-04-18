from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any

import pandas as pd

from vis_app.nl2viz import ChartSpec, chart_spec_from_dict


@dataclass
class LLMConfig:
    enabled: bool = False
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: float = 20.0
    generate_summary: bool = True

    def is_ready(self) -> bool:
        return bool(self.api_key.strip()) and bool(self.model.strip())


def default_llm_config() -> LLMConfig:
    return LLMConfig(
        enabled=False,
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
        model=os.getenv("OPENAI_MODEL", ""),
        timeout=20.0,
        generate_summary=True,
    )


def dataset_context(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = [column for column in df.columns if column not in numeric_columns]
    preview_rows = df.head(5).astype(str).to_dict(orient="records")
    return {
        "columns": df.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "preview_rows": preview_rows,
    }


def _extract_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM 没有返回有效 JSON。")
    return json.loads(text[start : end + 1])


def _normalize_base_url(base_url: str) -> str | None:
    value = base_url.strip()
    if not value:
        return None
    return value.rstrip("/")


def _is_chat_unsupported_error(text: str) -> bool:
    lowered = text.lower()
    return "/v1/chat/completions endpoint not supported" in lowered or "endpoint not supported" in lowered


def _friendly_llm_error(exc: Exception) -> RuntimeError:
    text = str(exc)
    lowered = text.lower()

    if _is_chat_unsupported_error(text):
        return RuntimeError(
            "当前模型通道不支持 `/v1/chat/completions`。程序会自动尝试 `responses` 接口；如果仍失败，通常表示该模型或网关本身不兼容。"
        )
    if "401" in lowered or "unauthorized" in lowered or "invalid api key" in lowered:
        return RuntimeError("API Key 无效，或当前接口不接受这组鉴权信息。")
    if "404" in lowered or "not found" in lowered:
        return RuntimeError("Base URL 或接口路径不正确，服务端没有找到对应接口。")
    if "timeout" in lowered:
        return RuntimeError("接口请求超时，请检查网络、网关响应速度或适当增大超时时间。")
    return RuntimeError(text)


def _build_client(config: LLMConfig):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("当前环境未安装 `openai` 包，请先执行 `uv pip install -r requirements.txt`。") from exc

    if not config.is_ready():
        raise RuntimeError("LLM 配置不完整，请至少填写模型名称和 API Key。")

    kwargs: dict[str, Any] = {
        "api_key": config.api_key.strip(),
        "timeout": float(config.timeout),
    }
    normalized = _normalize_base_url(config.base_url)
    if normalized:
        kwargs["base_url"] = normalized
    return OpenAI(**kwargs)


def _extract_text_from_responses_output(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text).strip()

    parts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(str(text))
    return "\n".join(part for part in parts if part).strip()


def _create_text_response(
    client: Any,
    *,
    model: str,
    system_prompt: str,
    user_content: str,
    temperature: float,
    max_output_tokens: int | None = None,
) -> tuple[str, str]:
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        content = response.choices[0].message.content or ""
        return str(content).strip(), "chat.completions"
    except Exception as exc:
        if not _is_chat_unsupported_error(str(exc)):
            raise

        response = client.responses.create(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_content}]},
            ],
        )
        content = _extract_text_from_responses_output(response)
        return content, "responses"


def test_llm_connection(config: LLMConfig) -> str:
    try:
        client = _build_client(config)
        content, endpoint = _create_text_response(
            client,
            model=config.model.strip(),
            system_prompt="You are a connection test endpoint. Reply briefly.",
            user_content="Reply with: connection ok",
            temperature=0,
            max_output_tokens=24,
        )
        if not content:
            raise RuntimeError("接口返回为空。")
        return f"{content} | endpoint={endpoint}"
    except Exception as exc:
        raise _friendly_llm_error(exc) from exc


def infer_chart_spec_with_llm(
    prompt: str,
    df: pd.DataFrame,
    config: LLMConfig,
    previous: ChartSpec | None = None,
) -> tuple[ChartSpec, str]:
    try:
        client = _build_client(config)

        previous_payload = None
        if previous:
            previous_payload = {
                "chart_type": previous.chart_type,
                "x": previous.x,
                "y": previous.y,
                "color": previous.color,
                "agg": previous.agg,
                "title": previous.title,
                "filters": previous.filters,
            }

        system_prompt = """
你是一个数据可视化分析助手。你的任务是把用户自然语言需求转换为图表配置 JSON。
必须只返回一个 JSON 对象，不要返回 markdown，不要解释。

JSON 字段要求：
- chart_type: 只能是 bar, line, scatter, pie, heatmap
- x: x 轴字段名或 null
- y: y 轴字段名或 null
- color: 着色字段名或 null
- agg: 只能是 sum, mean, count
- title: 图表标题
- filters: 数组，元素格式为 {"column": "...", "value": "..."}
- rationale: 简短说明为什么选这个图表
- insight: 简短说明当前图表关注点和下一步建议

规则：
- 只能使用提供的数据字段名，不要杜撰字段。
- 如果用户在做增量修改，尽量参考 previous_chart_spec。
- 如果是相关性分析，优先 scatter 或 heatmap。
- 如果是趋势分析，优先 line。
- 如果是类别对比，优先 bar。
- 如果是占比结构，优先 pie。
""".strip()

        user_payload = {
            "user_prompt": prompt,
            "dataset": dataset_context(df),
            "previous_chart_spec": previous_payload,
        }

        content, endpoint = _create_text_response(
            client,
            model=config.model.strip(),
            system_prompt=system_prompt,
            user_content=json.dumps(user_payload, ensure_ascii=False),
            temperature=0.2,
            max_output_tokens=700,
        )
        data = _extract_json_object(content)
        spec = chart_spec_from_dict(data, df, previous=previous)
        note = f"LLM 解析已启用，当前请求使用 {endpoint} 接口完成。"
        return spec, note
    except Exception as exc:
        raise _friendly_llm_error(exc) from exc


def generate_llm_summary(
    prompt: str,
    df: pd.DataFrame,
    spec: ChartSpec,
    summary_df: pd.DataFrame,
    config: LLMConfig,
) -> str:
    try:
        client = _build_client(config)
        payload = {
            "user_prompt": prompt,
            "chart_spec": {
                "chart_type": spec.chart_type,
                "x": spec.x,
                "y": spec.y,
                "color": spec.color,
                "agg": spec.agg,
                "filters": spec.filters,
                "title": spec.title,
            },
            "dataset_overview": {
                "row_count": int(df.shape[0]),
                "column_count": int(df.shape[1]),
                "columns": df.columns.tolist(),
            },
            "chart_summary_preview": summary_df.head(12).astype(str).to_dict(orient="records"),
        }
        content, _ = _create_text_response(
            client,
            model=config.model.strip(),
            system_prompt="你是数据可视化解读助手。请基于给定图表结果输出简洁中文摘要，控制在 3 条以内，每条一句，强调趋势、异常或下一步建议。",
            user_content=json.dumps(payload, ensure_ascii=False),
            temperature=0.2,
            max_output_tokens=220,
        )
        return content.strip()
    except Exception as exc:
        raise _friendly_llm_error(exc) from exc
