"""CF（キャッシュフロー）ビュー - サンキー・ウォーターフォール。"""

import streamlit as st

from utils.data_loader import load_company_info, load_cf, get_period_label
from utils.charts import create_cf_sankey, create_waterfall
from utils.tooltips import CF_TOOLTIPS

st.set_page_config(page_title="CF キャッシュフロー", page_icon="📊", layout="wide")

code = st.session_state.get("selected_code", "5139")
info = load_company_info(code)
st.title(f"CF キャッシュフロー - {info['name']}")

cf = load_cf(code)
periods = cf["期"].tolist()
selected_period = st.selectbox("表示期間", periods[::-1], format_func=get_period_label)
row = cf[cf["期"] == selected_period].iloc[0]
period_label = get_period_label(selected_period)

tab_sankey, tab_waterfall, tab_table = st.tabs(
    ["サンキーダイアグラム", "ウォーターフォール", "データテーブル"]
)

# --- サンキーダイアグラム ---
with tab_sankey:
    st.subheader(f"キャッシュフローの流れ ({period_label})")
    fig = create_cf_sankey(row, period_label)
    st.plotly_chart(fig, use_container_width=True)

    # CF分類の解説
    with st.expander("キャッシュフロー項目の解説"):
        for key, desc in CF_TOOLTIPS.items():
            st.markdown(f"**{key}**: {desc}")

    # CFタイプ分析
    st.subheader("CFパターン分析")
    op_positive = row["営業CF"] > 0
    inv_negative = row["投資CF"] < 0
    fin_negative = row["財務CF"] < 0

    if op_positive and inv_negative and fin_negative:
        pattern = "優良型"
        desc = "本業で稼いだ資金で投資と借入返済・配当を行っている健全なパターン。"
    elif op_positive and inv_negative and not fin_negative:
        pattern = "積極投資型"
        desc = "本業の稼ぎに加え、借入で資金調達し積極的に投資している成長企業のパターン。"
    elif op_positive and not inv_negative and fin_negative:
        pattern = "リストラ型"
        desc = "本業で稼ぎつつ、資産売却で投資回収し借入返済に充てているパターン。"
    else:
        pattern = "その他"
        desc = "一般的な分類に当てはまらないパターン。個別の事情を確認してください。"

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("CFパターン", pattern)
    with col2:
        st.info(desc)

# --- ウォーターフォール ---
with tab_waterfall:
    st.subheader(f"現金残高の変動 ({period_label})")

    cats = ["期首現金", "営業CF", "投資CF", "財務CF", "期末現金"]
    vals = [
        row["期首現金"],
        row["営業CF"],
        row["投資CF"],
        row["財務CF"],
        row["期末現金"],
    ]
    measures = ["absolute", "relative", "relative", "relative", "total"]

    fig = create_waterfall(cats, vals, f"現金残高ブリッジ ({period_label})", measures)
    st.plotly_chart(fig, use_container_width=True)

    # 数値サマリー
    st.subheader("数値サマリー")
    cols = st.columns(3)
    with cols[0]:
        st.metric("営業CF", f"{int(row['営業CF']):+,} 百万円")
    with cols[1]:
        st.metric("投資CF", f"{int(row['投資CF']):+,} 百万円")
    with cols[2]:
        st.metric("財務CF", f"{int(row['財務CF']):+,} 百万円")

    fcf = row["営業CF"] + row["投資CF"]
    st.metric("フリーキャッシュフロー (営業CF + 投資CF)", f"{int(fcf):+,} 百万円")

# --- データテーブル ---
with tab_table:
    st.subheader("CF データテーブル")
    display_df = cf.copy()
    display_df["期"] = display_df["期"].apply(get_period_label)
    display_df = display_df.set_index("期")
    st.dataframe(
        display_df.style.format("{:,.0f}"),
        use_container_width=True,
    )
