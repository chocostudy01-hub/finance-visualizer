"""ダッシュボード - サマリーカードと主要経営指標。"""

import streamlit as st

from utils.data_loader import (
    load_company_info,
    load_pl,
    load_bs,
    load_cf,
    calc_yoy_change,
    get_period_label,
)
from utils.charts import create_gauge
from utils.tooltips import METRIC_TOOLTIPS

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

code = st.session_state.get("selected_code", "5139")
info = load_company_info(code)
st.title(f"Dashboard - {info['name']} ({info['code']})")

# データ読み込み
pl = load_pl(code)
bs = load_bs(code)
cf = load_cf(code)

# 期間選択
periods = pl["期"].tolist()
selected_period = st.selectbox(
    "表示期間",
    periods[::-1],
    format_func=get_period_label,
)

row_pl = pl[pl["期"] == selected_period].iloc[0]
row_bs = bs[bs["期"] == selected_period].iloc[0]
row_cf = cf[cf["期"] == selected_period].iloc[0]
period_label = get_period_label(selected_period)

# 前年データ取得
idx = periods.index(selected_period)
has_prev = idx > 0

# --- サマリーカード ---
st.subheader("業績サマリー")

metrics = [
    ("営業収益", row_pl["営業収益"]),
    ("営業利益", row_pl["営業利益"]),
    ("経常利益", row_pl["経常利益"]),
    ("当期純利益", row_pl["当期純利益"]),
]

cols = st.columns(4)
for i, (label, value) in enumerate(metrics):
    with cols[i]:
        if has_prev:
            prev_row = pl[pl["期"] == periods[idx - 1]].iloc[0]
            delta = value - prev_row[label]
            delta_pct = (delta / prev_row[label]) * 100 if prev_row[label] != 0 else 0
            st.metric(
                label=label,
                value=f"{int(value):,} 百万円",
                delta=f"{delta:+,.0f} ({delta_pct:+.1f}%)",
            )
        else:
            st.metric(label=label, value=f"{int(value):,} 百万円")

st.divider()

# --- 経営指標 ---
st.subheader("主要経営指標")

op_margin = (row_pl["営業利益"] / row_pl["営業収益"]) * 100 if row_pl["営業収益"] else 0
gp_margin = (row_pl["売上総利益"] / row_pl["営業収益"]) * 100 if row_pl["営業収益"] else 0
equity_ratio = (row_bs["純資産合計"] / row_bs["資産合計"]) * 100 if row_bs["資産合計"] else 0
roe = (row_pl["当期純利益"] / row_bs["純資産合計"]) * 100 if row_bs["純資産合計"] else 0
roa = (row_pl["当期純利益"] / row_bs["資産合計"]) * 100 if row_bs["資産合計"] else 0

indicators = [
    ("営業利益率", op_margin, "%", [(0, 10, "#FFCDD2"), (10, 20, "#FFF9C4"), (20, 50, "#C8E6C9")]),
    ("売上総利益率", gp_margin, "%", [(0, 30, "#FFCDD2"), (30, 60, "#FFF9C4"), (60, 100, "#C8E6C9")]),
    ("自己資本比率", equity_ratio, "%", [(0, 30, "#FFCDD2"), (30, 50, "#FFF9C4"), (50, 100, "#C8E6C9")]),
    ("ROE", roe, "%", [(0, 5, "#FFCDD2"), (5, 10, "#FFF9C4"), (10, 40, "#C8E6C9")]),
    ("ROA", roa, "%", [(0, 3, "#FFCDD2"), (3, 5, "#FFF9C4"), (5, 30, "#C8E6C9")]),
]

cols = st.columns(len(indicators))
for i, (name, val, suffix, ranges) in enumerate(indicators):
    with cols[i]:
        fig = create_gauge(round(val, 1), name, suffix, ranges)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(METRIC_TOOLTIPS.get(name, ""))

st.divider()

# --- CF概要 ---
st.subheader("キャッシュフロー概要")
cf_cols = st.columns(4)
cf_items = [
    ("営業CF", row_cf["営業CF"]),
    ("投資CF", row_cf["投資CF"]),
    ("財務CF", row_cf["財務CF"]),
    ("期末現金", row_cf["期末現金"]),
]
for i, (label, value) in enumerate(cf_items):
    with cf_cols[i]:
        st.metric(label=label, value=f"{int(value):,} 百万円")

st.divider()
st.caption(f"データ期間: {period_label}　|　単位: 百万円")
