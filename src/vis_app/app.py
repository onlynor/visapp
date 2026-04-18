from __future__ import annotations

from pathlib import Path
import os

from PIL import Image
import streamlit as st


LOGO_PATH = Path("assets/images/logo.png")
FRONTEND_PASSWORD = os.getenv("FRONTEND_PASSWORD", "24343")

PAGE_CSS = """
<style>
    :root {
        --bg-1: #f6efe2;
        --bg-2: #edf5ef;
        --ink-1: #1a2b24;
        --ink-2: #526158;
        --line: rgba(46, 72, 60, 0.12);
        --card: rgba(255, 252, 246, 0.92);
        --accent: #346f5a;
        --accent-soft: #dfefe7;
        --shadow: 0 18px 44px rgba(62, 76, 66, 0.10);
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(239, 226, 188, 0.45), transparent 20%),
            radial-gradient(circle at 88% 12%, rgba(210, 230, 219, 0.7), transparent 22%),
            linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
    }
    .hero-card {
        padding: 1.35rem 1.45rem 1.15rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(255, 252, 246, 0.96), rgba(248, 252, 249, 0.90));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        border: 1px solid rgba(52, 111, 90, 0.10);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.85rem;
    }
    .hero-title {
        margin: 0;
        color: var(--ink-1);
        font-size: clamp(1.9rem, 4vw, 3rem);
        line-height: 1.08;
        font-weight: 800;
        word-break: break-word;
    }
    .hero-copy {
        margin: 0.62rem 0 0;
        color: var(--ink-2);
        font-size: 1rem;
        line-height: 1.65;
        max-width: 780px;
    }
    .hero-meta {
        margin-top: 0.9rem;
        color: var(--ink-2);
        font-size: 0.88rem;
    }
    .intro-card {
        padding: 1.05rem 1.1rem;
        border-radius: 22px;
        background: var(--card);
        border: 1px solid var(--line);
        box-shadow: 0 10px 26px rgba(62, 76, 66, 0.06);
        margin-bottom: 1rem;
    }
    .hint-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.85rem;
    }
    .hint-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        background: rgba(255, 249, 238, 0.92);
        border: 1px solid var(--line);
        color: var(--ink-2);
        font-size: 0.82rem;
    }
    .empty-panel {
        padding: 1.2rem 1.15rem 1.05rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(255, 252, 246, 0.96), rgba(248, 252, 249, 0.90));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }
    .empty-kicker {
        display: inline-flex;
        padding: 0.28rem 0.66rem;
        border-radius: 999px;
        background: rgba(239, 226, 188, 0.45);
        color: var(--ink-1);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }
    .empty-title {
        margin: 0;
        color: var(--ink-1);
        font-size: clamp(1.35rem, 3vw, 1.8rem);
        line-height: 1.15;
        font-weight: 800;
    }
    .empty-copy {
        margin: 0.58rem 0 0;
        color: var(--ink-2);
        font-size: 0.98rem;
        line-height: 1.65;
        max-width: 760px;
    }
    .empty-list {
        display: grid;
        gap: 0.55rem;
        margin-top: 0.9rem;
    }
    .empty-item {
        padding: 0.72rem 0.82rem;
        border-radius: 16px;
        background: rgba(255, 249, 238, 0.86);
        border: 1px solid rgba(46, 72, 60, 0.08);
        color: var(--ink-2);
        font-size: 0.9rem;
    }
    .auth-shell {
        min-height: calc(100vh - 5rem);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .auth-title {
        margin: 0;
        color: var(--ink-1);
        font-size: clamp(1.55rem, 3vw, 2.1rem);
        line-height: 1.16;
        font-weight: 800;
        word-break: break-word;
        overflow-wrap: anywhere;
    }
    .auth-copy {
        margin: 0.7rem 0 1.15rem;
        color: var(--ink-2);
        font-size: 0.98rem;
        line-height: 1.6;
    }
    .auth-field-label {
        margin: 0 0 0.42rem;
        color: var(--ink-1);
        font-size: 0.92rem;
        font-weight: 700;
    }
    .auth-wrap {
        max-width: 640px;
        margin: 0 auto;
        padding: 0 0.6rem;
        width: 100%;
    }
    .auth-card {
        padding: 1.7rem 1.55rem 1.35rem;
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(255, 252, 246, 0.98), rgba(248, 252, 249, 0.94));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }
    .auth-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        border: 1px solid rgba(52, 111, 90, 0.12);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    .auth-title {
        margin: 0;
        color: var(--ink-1);
        font-size: clamp(1.65rem, 3.4vw, 2.3rem);
        line-height: 1.18;
        font-weight: 800;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .auth-copy {
        margin: 0.72rem 0 1.15rem;
        color: var(--ink-2);
        font-size: 0.98rem;
        line-height: 1.62;
    }
    .auth-input-wrap {
        max-width: 420px;
        margin: 0 auto;
    }
</style>
"""


@st.cache_resource
def _load_page_icon():
    if LOGO_PATH.exists():
        try:
            image = Image.open(LOGO_PATH)
            image.load()
            return image
        except Exception:
            return None
    return None


def _get_data_utils():
    from vis_app import data_utils

    return data_utils


def _get_nl2viz():
    from vis_app import nl2viz

    return nl2viz


def _get_charts():
    from vis_app import charts

    return charts


def _get_llm():
    from vis_app import llm

    return llm


def _init_state() -> None:
    st.session_state.setdefault("raw_df", None)
    st.session_state.setdefault("clean_df", None)
    st.session_state.setdefault("cleaning_notes", [])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("last_spec", None)
    st.session_state.setdefault("llm_config", None)
    st.session_state.setdefault("llm_connection_status", "")
    st.session_state.setdefault("llm_connection_ok", None)
    st.session_state.setdefault("show_project_intro", False)
    st.session_state.setdefault("is_authenticated", False)
    st.session_state.setdefault("auth_error", "")
    st.session_state.setdefault("ui_message", "")
    st.session_state.setdefault("ui_message_type", "info")


def _set_ui_message(message: str, level: str = "info") -> None:
    st.session_state.ui_message = message
    st.session_state.ui_message_type = level


def _render_ui_message() -> None:
    message = st.session_state.ui_message
    if not message:
        return
    level = st.session_state.ui_message_type
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def _safe_user_message(exc: Exception, fallback: str) -> str:
    text = str(exc).strip()
    if not text or len(text) > 180:
        return fallback
    blocked_tokens = ["Traceback", 'File "', "site-packages", "E:\\", "C:\\", "line "]
    if any(token in text for token in blocked_tokens):
        return fallback
    return text


def _reset_after_dataset_change() -> None:
    st.session_state.clean_df = None
    st.session_state.cleaning_notes = []
    st.session_state.history = []
    st.session_state.last_spec = None


def _render_header() -> None:
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">Visual Insight Studio</div>
            <h1 class="hero-title">自然语言数据可视化工作台</h1>
            <p class="hero-copy">上传数据后，直接用自然语言生成图表、查看结果摘要，并根据需要继续做迭代分析。</p>
            <div class="hero-meta">支持 CSV / Excel 数据上传、多轮图表修改、结果导出与 OpenAI 兼容接口增强分析。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def _render_project_intro() -> None:
    if not st.session_state.show_project_intro:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("简要说明已收起，可按需重新展开。")
        with col2:
            if st.button("展开说明", use_container_width=True):
                st.session_state.show_project_intro = True
        return

    st.markdown('<div class="intro-card">', unsafe_allow_html=True)
    st.markdown("### 使用说明")
    st.write("1. 上传 CSV 或 Excel 数据文件。")
    st.write("2. 先预览数据，再按需执行基础清洗。")
    st.write("3. 通过自然语言直接生成图表，或继续做迭代修改。")
    st.write("4. 可导出图表 HTML 和汇总结果 CSV。")
    st.markdown(
        """
        <div class="hint-row">
            <span class="hint-chip">规则分析默认可用</span>
            <span class="hint-chip">支持多轮连续修改</span>
            <span class="hint-chip">可选开启 LLM 驱动分析</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    close_col1, close_col2 = st.columns([3, 1])
    with close_col2:
        if st.button("收起说明", use_container_width=True):
            st.session_state.show_project_intro = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _handle_load_sample() -> None:
    try:
        with st.spinner("正在加载示例数据..."):
            st.session_state.raw_df = _get_data_utils().load_sample_dataset(Path("data/sample_sales.csv"))
        _reset_after_dataset_change()
        _set_ui_message("示例数据已加载。", "success")
    except Exception as exc:
        _set_ui_message(_safe_user_message(exc, "示例数据加载失败，请稍后重试。"), "error")


def _handle_uploaded_file(uploaded) -> None:
    try:
        with st.spinner("正在读取上传文件..."):
            st.session_state.raw_df = _get_data_utils().load_dataset(uploaded)
        _reset_after_dataset_change()
        _set_ui_message("数据文件读取成功。", "success")
    except Exception as exc:
        _set_ui_message(_safe_user_message(exc, "文件读取失败，请确认文件格式和内容是否正确。"), "error")


def _handle_clean_data(missing_strategy: str, outlier_strategy: str) -> None:
    try:
        with st.spinner("正在执行数据清洗..."):
            cleaned, notes = _get_data_utils().clean_dataset(
                st.session_state.raw_df,
                missing_strategy=missing_strategy,
                outlier_strategy=outlier_strategy,
            )
        st.session_state.clean_df = cleaned
        st.session_state.cleaning_notes = notes
        st.session_state.history = []
        st.session_state.last_spec = None
        _set_ui_message("数据清洗已完成。", "success")
    except Exception as exc:
        _set_ui_message(_safe_user_message(exc, "数据清洗失败，请检查数据内容后重试。"), "error")


def _handle_test_connection(config) -> None:
    try:
        with st.spinner("正在测试接口连接..."):
            message = _get_llm().test_llm_connection(config)
        st.session_state.llm_connection_ok = True
        st.session_state.llm_connection_status = f"连接成功：{message}"
    except Exception as exc:
        st.session_state.llm_connection_ok = False
        safe_message = _safe_user_message(exc, "连接失败，请检查模型、接口地址和 API Key。")
        st.session_state.llm_connection_status = f"连接失败：{safe_message}"


def _render_stat_strip() -> None:
    raw_df = st.session_state.raw_df
    clean_df = st.session_state.clean_df
    rows = raw_df.shape[0] if raw_df is not None else 0
    cols = raw_df.shape[1] if raw_df is not None else 0
    cleaned_rows = clean_df.shape[0] if clean_df is not None else 0
    history_len = len(st.session_state.history)
    st.markdown(
        f"""
        <div class="stat-strip">
            <div class="stat-card"><div class="stat-label">原始记录数</div><div class="stat-value">{rows}</div></div>
            <div class="stat-card"><div class="stat-label">字段数量</div><div class="stat-value">{cols}</div></div>
            <div class="stat-card"><div class="stat-label">清洗后记录数</div><div class="stat-value">{cleaned_rows}</div></div>
            <div class="stat-card"><div class="stat-label">迭代次数</div><div class="stat-value">{history_len}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_dataset_overview() -> None:
    if st.session_state.raw_df is None:
        st.info("请先上传数据，或加载示例数据。")
        return

    df = st.session_state.clean_df if st.session_state.clean_df is not None else st.session_state.raw_df
    profile = _get_data_utils().profile_dataset(df)

    with st.expander("数据预览", expanded=True):
        st.dataframe(df.head(50), use_container_width=True)

    with st.expander("字段类型", expanded=False):
        st.dataframe(profile.dtypes, use_container_width=True)

    with st.expander("缺失值统计", expanded=False):
        st.dataframe(profile.missing, use_container_width=True)

    if not profile.numeric_summary.empty:
        with st.expander("数值字段摘要", expanded=False):
            st.dataframe(profile.numeric_summary, use_container_width=True)


def _render_sidebar() -> None:
    st.sidebar.header("1. 数据输入")
    if st.sidebar.button("加载示例数据", use_container_width=True):
        _handle_load_sample()

    uploaded = st.sidebar.file_uploader("上传 CSV 或 Excel", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        _handle_uploaded_file(uploaded)

    if st.session_state.raw_df is None:
        st.sidebar.info("请先上传数据，或点击按钮加载示例数据。")
        return

    st.sidebar.success(
        f"当前数据集：{st.session_state.raw_df.shape[0]} 行 × {st.session_state.raw_df.shape[1]} 列"
    )

    st.sidebar.header("2. 数据清洗")
    missing_strategy = st.sidebar.selectbox(
        "缺失值处理",
        options=["median_mode", "mean_mode"],
        format_func=lambda x: "数值中位数 / 类别众数" if x == "median_mode" else "数值平均值 / 类别众数",
    )
    outlier_strategy = st.sidebar.selectbox(
        "异常值处理",
        options=["clip_iqr", "keep"],
        format_func=lambda x: "IQR 截尾" if x == "clip_iqr" else "保留原值",
    )
    if st.sidebar.button("执行清洗", type="primary", use_container_width=True):
        _handle_clean_data(missing_strategy, outlier_strategy)

    st.sidebar.header("3. LLM 驱动分析")
    with st.sidebar.expander("OpenAI 兼容接口", expanded=False):
        st.caption("仅支持 OpenAI 兼容接口，不支持 Anthropic 原生接口。")
        st.caption("当前优先使用 /v1/chat/completions，必要时会自动尝试 /v1/responses。")

        config = st.session_state.llm_config or _get_llm().default_llm_config()
        config.enabled = st.toggle("LLM 驱动分析", value=config.enabled)
        config.base_url = st.text_input(
            "Base URL",
            value=config.base_url,
            placeholder="请填写 OpenAI 兼容接口根地址",
            help="请填写接口根地址，不要填写网页首页地址。",
        )
        config.model = st.text_input("模型名称", value=config.model, placeholder="请输入兼容模型名称")
        config.api_key = st.text_input("API Key", value=config.api_key, type="password", placeholder="请输入 API Key")
        config.generate_summary = st.toggle("生成结果摘要", value=config.generate_summary)
        st.session_state.llm_config = config

        if st.button("测试连接", use_container_width=True):
            _handle_test_connection(config)

        if st.session_state.llm_connection_ok is True:
            st.success(st.session_state.llm_connection_status)
        elif st.session_state.llm_connection_ok is False:
            st.error(st.session_state.llm_connection_status)

        if config.enabled and config.is_ready():
            st.success("配置已完成，可以直接使用 LLM 驱动分析。")
        elif config.enabled:
            st.warning("已开启 LLM 驱动分析，但当前配置还不完整。")
        else:
            st.info("不填写接口信息也可以直接使用规则分析。")


def _run_prompt(prompt: str) -> None:
    df = st.session_state.clean_df if st.session_state.clean_df is not None else st.session_state.raw_df
    previous = st.session_state.last_spec
    nl2viz = _get_nl2viz()
    charts = _get_charts()

    engine = "规则分析"
    engine_note = "当前结果由规则分析生成。"
    llm_summary = ""
    spec = None
    llm_config = st.session_state.llm_config

    try:
        if llm_config and llm_config.enabled and llm_config.is_ready():
            try:
                with st.spinner("正在使用 LLM 解析指令..."):
                    spec, engine_note = _get_llm().infer_chart_spec_with_llm(prompt, df, llm_config, previous=previous)
                engine = "LLM 驱动分析"
            except Exception:
                spec = nl2viz.infer_chart_spec(prompt, df, previous=previous)
                engine = "规则分析"
                engine_note = "LLM 解析失败，已自动回退到规则分析。"
        else:
            spec = nl2viz.infer_chart_spec(prompt, df, previous=previous)

        with st.spinner("正在生成图表..."):
            fig, filtered, summary = charts.build_figure(df, spec)

        if engine == "LLM 驱动分析" and llm_config and llm_config.generate_summary:
            try:
                with st.spinner("正在生成结果摘要..."):
                    llm_summary = _get_llm().generate_llm_summary(prompt, filtered, spec, summary, llm_config)
            except Exception:
                llm_summary = ""

        st.session_state.last_spec = spec
        st.session_state.history.append(
            {
                "prompt": prompt,
                "spec": spec,
                "figure": fig,
                "summary": summary,
                "filtered_rows": len(filtered),
                "engine": engine,
                "engine_note": engine_note,
                "llm_summary": llm_summary,
            }
        )
        _set_ui_message("图表已生成。", "success")
    except Exception as exc:
        safe_message = _safe_user_message(exc, "当前指令无法生成有效图表，请换一种更明确的描述再试。")
        _set_ui_message(safe_message, "error")


def _render_generation_area() -> None:
    st.subheader("自然语言生成")
    prompt = st.text_area(
        "输入你的可视化指令",
        height=110,
        placeholder="例如：用家电相关数据做一个饼图，或生成各品类销售额柱状图并筛选地区为华东",
    )
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("生成 / 迭代图表", type="primary", use_container_width=True):
            if prompt.strip():
                _run_prompt(prompt)
            else:
                _set_ui_message("请输入自然语言指令后再生成图表。", "warning")
    with col2:
        if st.button("清空迭代记录", use_container_width=True):
            st.session_state.history = []
            st.session_state.last_spec = None
            _set_ui_message("历史记录已清空。", "info")


def _render_results() -> None:
    history = st.session_state.history
    if not history:
        st.info("输入自然语言指令后，这里会显示图表、说明和迭代记录。")
        return

    latest = history[-1]
    spec = latest["spec"]
    nl2viz = _get_nl2viz()

    left, right = st.columns([3.15, 1.85])
    with left:
        st.plotly_chart(latest["figure"], use_container_width=True)
    with right:
        if latest["engine"] == "LLM 驱动分析":
            st.success("当前结果由 LLM 驱动分析生成。")
        else:
            st.info("当前结果由规则分析生成。")

        st.markdown("### 图表说明")
        st.write(spec.rationale)
        st.write(spec.insight)
        st.caption(latest["engine_note"])
        st.caption(f"当前图表：{nl2viz.chart_type_name(spec.chart_type)} | 筛选后记录数：{latest['filtered_rows']}")

        if latest.get("llm_summary"):
            st.markdown("### 分析摘要")
            st.write(latest["llm_summary"])

        st.download_button(
            "导出图表 HTML",
            data=_get_charts().figure_to_html(latest["figure"]),
            file_name="chart_export.html",
            mime="text/html",
            use_container_width=True,
        )
        st.download_button(
            "导出汇总结果 CSV",
            data=latest["summary"].to_csv(index=False).encode("utf-8-sig"),
            file_name="chart_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with st.expander("本次图表对应的数据摘要", expanded=False):
        st.dataframe(latest["summary"], use_container_width=True)

    with st.expander("多轮迭代历史", expanded=False):
        for index, item in enumerate(reversed(history), start=1):
            item_spec = item["spec"]
            st.markdown(
                f"**第 {len(history) - index + 1} 轮** 指令：`{item['prompt']}` | 图表：`{nl2viz.chart_type_name(item_spec.chart_type)}` | 模式：`{item['engine']}`"
            )


def _render_notes() -> None:
    st.subheader("说明区")
    notes = st.session_state.cleaning_notes
    if notes:
        st.write("数据清洗记录：")
        for note in notes:
            st.write(f"- {note}")
    else:
        st.write("当前尚未执行数据清洗。")

    st.write("如需更复杂的分析，可在左侧填写兼容接口配置；不填写也可直接完成常规可视化操作。")


def _render_empty_state() -> None:
    st.subheader("开始使用")
    st.write("当前还没有载入数据。")
    st.write("你可以点击下方按钮加载示例数据，或在左侧上传 CSV / Excel 文件。")
    if st.button("加载示例数据", type="primary"):
        _handle_load_sample()
        st.rerun()



def _render_password_gate() -> bool:
    if st.session_state.is_authenticated:
        return True

    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="auth-badge">Visual Access</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="auth-title">访问验证</h2>', unsafe_allow_html=True)
    st.markdown('<p class="auth-copy">请输入访问密码后进入工作台。</p>', unsafe_allow_html=True)
    st.markdown('<div class="auth-input-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-field-label">访问密码</div>', unsafe_allow_html=True)

    password = st.text_input(
        "访问密码",
        type="password",
        placeholder="请输入密码",
        key="password_input",
        label_visibility="collapsed",
    )
    submitted = st.button("进入工作台", type="primary", use_container_width=True)

    if submitted:
        entered = str(password or "").strip()
        expected = str(FRONTEND_PASSWORD or "").strip() or "24343"
        if entered == expected:
            st.session_state.is_authenticated = True
            st.session_state.auth_error = ""
            st.rerun()
        else:
            st.session_state.auth_error = "密码错误，请重新输入。"

    if st.session_state.auth_error:
        st.error(st.session_state.auth_error)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return False



def main() -> None:
    st.set_page_config(page_title="自然语言可视化工作台", page_icon=_load_page_icon(), layout="wide")
    _init_state()

    if not _render_password_gate():
        return

    _render_header()
    _render_ui_message()

    if st.session_state.raw_df is None:
        _render_empty_state()
        _render_sidebar()
        return

    _render_sidebar()
    _render_project_intro()
    _render_stat_strip()
    _render_dataset_overview()
    _render_generation_area()
    _render_results()
    _render_notes()
