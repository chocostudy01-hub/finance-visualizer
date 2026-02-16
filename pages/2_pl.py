"""P/L（損益計算書）ビュー - サンキー・ウォーターフォール・セグメント。"""

import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_company_info,
    load_pl,
    load_segment,
    load_factors,
    get_period_label,
)
from utils.charts import create_pl_sankey, create_waterfall, create_treemap
from utils.tooltips import PL_TOOLTIPS

st.set_page_config(page_title="P/L 損益計算書", page_icon="📊", layout="wide")

code = st.session_state.get("selected_code", "5139")
info = load_company_info(code)
st.title(f"P/L 損益計算書 - {info['name']}")

pl = load_pl(code)
segment = load_segment(code)
factors = load_factors(code)

periods = pl["期"].tolist()
selected_period = st.selectbox("表示期間", periods[::-1], format_func=get_period_label)
row = pl[pl["期"] == selected_period].iloc[0]
period_label = get_period_label(selected_period)
idx = periods.index(selected_period)

# --- タブ構成 ---
tab_sankey, tab_waterfall, tab_segment, tab_table = st.tabs(
    ["サンキーダイアグラム", "ウォーターフォール", "セグメント", "データテーブル"]
)

# --- サンキーダイアグラム ---
with tab_sankey:
    st.subheader("収益→費用→利益フロー")
    fig = create_pl_sankey(row, period_label)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("項目の解説"):
        for key, desc in PL_TOOLTIPS.items():
            st.markdown(f"**{key}**: {desc}")

# --- ウォーターフォール ---
with tab_waterfall:
    if idx > 0:
        prev_row = pl[pl["期"] == periods[idx - 1]].iloc[0]
        prev_label = get_period_label(periods[idx - 1])

        st.subheader(f"営業利益の変動要因 ({prev_label} → {period_label})")

        # 変動要因データ取得
        period_factors = factors[factors["期"] == selected_period]

        if len(period_factors) > 0:
            cats = [f"{prev_label}\n営業利益"]
            vals = [prev_row["営業利益"]]
            measures = ["absolute"]

            for _, f_row in period_factors.iterrows():
                cats.append(f_row["要因"])
                # CSVの金額は文字列（+/-付き）なので変換
                amount_str = str(f_row["金額"]).replace(",", "").replace("−", "-").replace("+", "")
                vals.append(float(amount_str))
                measures.append("relative")

            cats.append(f"{period_label}\n営業利益")
            vals.append(row["営業利益"])
            measures.append("total")

            fig = create_waterfall(cats, vals, f"営業利益ブリッジ ({prev_label} → {period_label})", measures)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # 要因データがない場合はシンプルなウォーターフォール
            cats = [
                f"{prev_label}\n営業利益",
                "売上増減",
                "原価増減",
                "販管費増減",
                f"{period_label}\n営業利益",
            ]
            vals = [
                prev_row["営業利益"],
                row["営業収益"] - prev_row["営業収益"],
                -(row["売上原価"] - prev_row["売上原価"]),
                -(row["販管費"] - prev_row["販管費"]),
                row["営業利益"],
            ]
            measures = ["absolute", "relative", "relative", "relative", "total"]
            fig = create_waterfall(cats, vals, f"営業利益ブリッジ ({prev_label} → {period_label})", measures)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ウォーターフォールチャートは前年データが必要です。2期目以降を選択してください。")

# --- セグメント ---
with tab_segment:
    st.subheader("セグメント別売上構成")

    seg_data = segment[segment["期"] == selected_period]
    if len(seg_data) > 0:
        # ツリーマップ
        labels_tm = ["全社"] + seg_data["セグメント"].tolist()
        parents_tm = [""] + ["全社"] * len(seg_data)
        values_tm = [0] + seg_data["売上"].tolist()

        # 前年比計算
        color_vals = [0]
        if idx > 0:
            prev_seg = segment[segment["期"] == periods[idx - 1]]
            for _, s_row in seg_data.iterrows():
                prev_val = prev_seg[prev_seg["セグメント"] == s_row["セグメント"]]["売上"]
                if len(prev_val) > 0:
                    pct = ((s_row["売上"] - prev_val.iloc[0]) / prev_val.iloc[0]) * 100
                    color_vals.append(pct)
                else:
                    color_vals.append(0)
        else:
            color_vals = None

        fig = create_treemap(
            labels_tm, parents_tm, values_tm,
            f"セグメント別売上 ({period_label})",
            color_vals,
        )
        st.plotly_chart(fig, use_container_width=True)

        # セグメント別テーブル
        st.dataframe(
            seg_data[["セグメント", "売上", "営業利益"]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("セグメントデータがありません。")

# --- データテーブル ---
with tab_table:
    st.subheader("P/L データテーブル")
    display_cols = [c for c in pl.columns if c != "期"]
    display_df = pl.copy()
    display_df["期"] = display_df["期"].apply(get_period_label)
    display_df = display_df.set_index("期")
    st.dataframe(
        display_df.style.format("{:,.0f}"),
        use_container_width=True,
    )
