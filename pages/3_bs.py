"""B/S（貸借対照表）ビュー - ブロック図・前年比較・ドリルダウン。"""

import streamlit as st

from utils.data_loader import load_company_info, load_bs, get_period_label
from utils.charts import create_bs_block, create_waterfall
from utils.tooltips import BS_TOOLTIPS

st.set_page_config(page_title="B/S 貸借対照表", page_icon="📊", layout="wide")

code = st.session_state.get("selected_code", "5139")
info = load_company_info(code)
st.title(f"B/S 貸借対照表 - {info['name']}")

bs = load_bs(code)
periods = bs["期"].tolist()
selected_period = st.selectbox("表示期間", periods[::-1], format_func=get_period_label)
row = bs[bs["期"] == selected_period].iloc[0]
period_label = get_period_label(selected_period)
idx = periods.index(selected_period)

tab_block, tab_compare, tab_drill, tab_table = st.tabs(
    ["ブロック図", "2期比較", "ドリルダウン", "データテーブル"]
)

# --- ブロック図 ---
with tab_block:
    st.subheader(f"資産＝負債＋純資産 ({period_label})")
    fig = create_bs_block(row, period_label)
    st.plotly_chart(fig, use_container_width=True)

    # サマリー
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("資産合計", f"{int(row['資産合計']):,} 百万円")
    with col2:
        st.metric("負債合計", f"{int(row['負債合計']):,} 百万円")
    with col3:
        st.metric("純資産合計", f"{int(row['純資産合計']):,} 百万円")

    with st.expander("項目の解説"):
        for key, desc in BS_TOOLTIPS.items():
            st.markdown(f"**{key}**: {desc}")

# --- 2期比較 ---
with tab_compare:
    if idx > 0:
        prev_period = periods[idx - 1]
        prev_row = bs[bs["期"] == prev_period].iloc[0]
        prev_label = get_period_label(prev_period)

        st.subheader(f"{prev_label} vs {period_label}")

        col1, col2 = st.columns(2)
        with col1:
            fig1 = create_bs_block(prev_row, prev_label)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = create_bs_block(row, period_label)
            st.plotly_chart(fig2, use_container_width=True)

        # 主要項目の増減
        st.subheader("主要項目の増減")
        compare_items = ["資産合計", "流動資産合計", "固定資産合計",
                         "負債合計", "純資産合計", "現金及び預金", "利益剰余金"]
        cats = []
        vals = []
        for item in compare_items:
            cats.append(item)
            vals.append(row[item] - prev_row[item])

        measures = ["relative"] * len(cats)
        fig = create_waterfall(
            cats, vals,
            f"B/S主要項目の増減 ({prev_label} → {period_label})",
            measures,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("2期比較は前年データが必要です。2期目以降を選択してください。")

# --- ドリルダウン ---
with tab_drill:
    st.subheader("資産内訳の詳細")

    drill_category = st.radio(
        "表示カテゴリ",
        ["流動資産", "固定資産", "負債", "純資産"],
        horizontal=True,
    )

    if drill_category == "流動資産":
        items = {"現金及び預金": row["現金及び預金"], "売掛金": row["売掛金"],
                 "その他流動資産": row["その他流動資産"]}
        total = row["流動資産合計"]
    elif drill_category == "固定資産":
        items = {"有形固定資産": row["有形固定資産"], "無形固定資産": row["無形固定資産"],
                 "投資その他": row["投資その他"]}
        total = row["固定資産合計"]
    elif drill_category == "負債":
        items = {"買掛金": row["買掛金"], "その他流動負債": row["その他流動負債"],
                 "長期借入金": row["長期借入金"], "その他固定負債": row["その他固定負債"]}
        total = row["負債合計"]
    else:
        items = {"資本金": row["資本金"], "資本剰余金": row["資本剰余金"],
                 "利益剰余金": row["利益剰余金"]}
        total = row["純資産合計"]

    st.markdown(f"**{drill_category} 合計: {int(total):,} 百万円**")

    for name, val in items.items():
        pct = (val / total * 100) if total else 0
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(min(pct / 100, 1.0), text=f"{name}: {int(val):,} 百万円")
        with col2:
            st.markdown(f"**{pct:.1f}%**")

# --- データテーブル ---
with tab_table:
    st.subheader("B/S データテーブル")
    display_df = bs.copy()
    display_df["期"] = display_df["期"].apply(get_period_label)
    display_df = display_df.set_index("期")
    st.dataframe(
        display_df.style.format("{:,.0f}"),
        use_container_width=True,
    )
