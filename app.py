"""上場企業 財務ビジュアライザー - メインページ。"""

import streamlit as st

from utils.data_loader import list_companies, load_company_info

st.set_page_config(
    page_title="財務ビジュアライザー",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("上場企業 財務ビジュアライザー")
st.markdown("個人投資家向け - 財務諸表を直感的に可視化")

st.divider()

# 企業選択
companies = list_companies()
if not companies:
    st.error("data/ フォルダに企業データがありません。")
    st.stop()

# サイドバーに企業選択を配置（全ページ共通）
with st.sidebar:
    st.header("企業選択")
    options = {f"{c['code']} {c['name']}": c["code"] for c in companies}
    selected = st.selectbox("企業を選択", list(options.keys()))
    code = options[selected]
    st.session_state["selected_code"] = code

info = load_company_info(code)

# 企業情報カード
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader(f"{info['name']} ({info['code']})")
    st.markdown(f"**市場:** {info['market']}　|　**決算期:** {info['fiscal_label']}")
    st.markdown(f"**事業内容:** {info['description']}")
    if info.get("notes"):
        st.info(info["notes"])

with col2:
    st.metric("証券コード", info["code"])
    st.markdown(f"[企業サイト]({info['url']})")

st.divider()

# ページガイド
st.subheader("ページ一覧")

pages_info = [
    ("1 - Dashboard", "売上・利益のサマリーカードと主要経営指標ゲージを表示"),
    ("2 - P/L (損益計算書)", "サンキーダイアグラムで収益→費用→利益の流れを可視化。ウォーターフォールで前年比分析"),
    ("3 - B/S (貸借対照表)", "資産＝負債＋純資産のブロック図。2期並列比較で変化を把握"),
    ("4 - CF (キャッシュフロー)", "営業・投資・財務CFのサンキー図とウォーターフォール"),
    ("5 - Trend (時系列推移)", "4期分の折れ線グラフで売上・利益・指標の推移を分析"),
]

for page, desc in pages_info:
    st.markdown(f"**{page}**  \n{desc}")

st.divider()
st.caption("※ 推定値を含むデータがあります。有価証券報告書から正確な数値に差し替え可能です。")
