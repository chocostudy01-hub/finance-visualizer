"""時系列推移ビュー - 折れ線グラフとトレンド分析。"""

import streamlit as st

from utils.data_loader import (
    load_company_info,
    load_pl,
    load_bs,
    load_cf,
    get_period_label,
)
from utils.charts import create_trend_chart

st.set_page_config(page_title="Trend 時系列推移", page_icon="📊", layout="wide")

code = st.session_state.get("selected_code", "5139")
info = load_company_info(code)
st.title(f"時系列推移 - {info['name']}")

pl = load_pl(code)
bs = load_bs(code)
cf = load_cf(code)

# --- 売上・利益推移 ---
st.subheader("売上・利益の推移")

revenue_cols = st.multiselect(
    "表示項目を選択",
    ["営業収益", "売上総利益", "営業利益", "経常利益", "当期純利益"],
    default=["営業収益", "営業利益", "当期純利益"],
)

if revenue_cols:
    fig = create_trend_chart(pl, revenue_cols, "売上・利益の推移")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 利益率推移 ---
st.subheader("利益率の推移")

pl_rates = pl.copy()
pl_rates["営業利益率"] = (pl_rates["営業利益"] / pl_rates["営業収益"] * 100).round(1)
pl_rates["売上総利益率"] = (pl_rates["売上総利益"] / pl_rates["営業収益"] * 100).round(1)
pl_rates["純利益率"] = (pl_rates["当期純利益"] / pl_rates["営業収益"] * 100).round(1)

fig = create_trend_chart(
    pl_rates,
    ["営業利益率", "売上総利益率", "純利益率"],
    "利益率の推移",
    unit="%",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 成長率推移 ---
st.subheader("前年比成長率")

pl_growth = pl.copy()
pl_growth["売上成長率"] = (pl_growth["営業収益"].pct_change() * 100).round(1)
pl_growth["営業利益成長率"] = (pl_growth["営業利益"].pct_change() * 100).round(1)
pl_growth["純利益成長率"] = (pl_growth["当期純利益"].pct_change() * 100).round(1)

# 最初の行はNaN
growth_df = pl_growth.dropna(subset=["売上成長率"]).reset_index(drop=True)

if len(growth_df) > 0:
    fig = create_trend_chart(
        growth_df,
        ["売上成長率", "営業利益成長率", "純利益成長率"],
        "前年比成長率の推移",
        unit="%",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- B/S推移 ---
st.subheader("B/S主要項目の推移")

bs_cols = st.multiselect(
    "B/S表示項目を選択",
    ["資産合計", "純資産合計", "負債合計", "現金及び預金", "利益剰余金"],
    default=["資産合計", "純資産合計", "現金及び預金"],
)

if bs_cols:
    fig = create_trend_chart(bs, bs_cols, "B/S主要項目の推移")
    st.plotly_chart(fig, use_container_width=True)

# 自己資本比率の推移
bs_ratio = bs.copy()
bs_ratio["自己資本比率"] = (bs_ratio["純資産合計"] / bs_ratio["資産合計"] * 100).round(1)

fig = create_trend_chart(bs_ratio, ["自己資本比率"], "自己資本比率の推移", unit="%")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- CF推移 ---
st.subheader("キャッシュフローの推移")

fig = create_trend_chart(cf, ["営業CF", "投資CF", "財務CF"], "キャッシュフローの推移")
st.plotly_chart(fig, use_container_width=True)

# FCF推移
cf_fcf = cf.copy()
cf_fcf["FCF"] = cf_fcf["営業CF"] + cf_fcf["投資CF"]

fig = create_trend_chart(cf_fcf, ["FCF", "期末現金"], "FCF・現金残高の推移")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- トレンドアノテーション ---
st.subheader("トレンドハイライト")

# 最新期と前期の比較
latest = pl.iloc[-1]
prev = pl.iloc[-2]
latest_label = get_period_label(latest["期"])

highlights = []

rev_growth = (latest["営業収益"] - prev["営業収益"]) / prev["営業収益"] * 100
highlights.append(f"売上高成長率 **{rev_growth:.1f}%** ({latest_label})")

op_growth = (latest["営業利益"] - prev["営業利益"]) / prev["営業利益"] * 100
highlights.append(f"営業利益成長率 **{op_growth:.1f}%** ({latest_label})")

op_margin = latest["営業利益"] / latest["営業収益"] * 100
prev_margin = prev["営業利益"] / prev["営業収益"] * 100
margin_change = op_margin - prev_margin
direction = "改善" if margin_change > 0 else "悪化"
highlights.append(f"営業利益率 **{op_margin:.1f}%** (前期比 {margin_change:+.1f}pt {direction})")

latest_bs = bs.iloc[-1]
equity_ratio = latest_bs["純資産合計"] / latest_bs["資産合計"] * 100
highlights.append(f"自己資本比率 **{equity_ratio:.1f}%**")

latest_cf = cf.iloc[-1]
fcf = latest_cf["営業CF"] + latest_cf["投資CF"]
highlights.append(f"FCF **{int(fcf):,} 百万円** (営業CF {int(latest_cf['営業CF']):,} + 投資CF {int(latest_cf['投資CF']):,})")

for h in highlights:
    st.markdown(f"- {h}")

st.divider()
st.caption("※ 推定値を含むデータがあります。有価証券報告書から正確な数値に差し替え可能です。")
