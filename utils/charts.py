"""Plotlyチャート生成関数群。"""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import pandas as pd


# 共通カラーパレット
COLORS = {
    "revenue": "#2196F3",
    "cost": "#FF5722",
    "profit": "#4CAF50",
    "expense": "#FF9800",
    "tax": "#9C27B0",
    "asset": "#2196F3",
    "liability": "#FF5722",
    "equity": "#4CAF50",
    "operating_cf": "#4CAF50",
    "investing_cf": "#FF9800",
    "financing_cf": "#9C27B0",
    "positive": "#4CAF50",
    "negative": "#FF5722",
    "total": "#2196F3",
    "subtotal": "#42A5F5",
}


def create_pl_sankey(row: pd.Series, period_label: str) -> go.Figure:
    """P/Lサンキーダイアグラムを生成する。

    Args:
        row: P/Lの1期分のデータ行。
        period_label: 表示用期間ラベル。

    Returns:
        Plotly Figure。
    """
    labels = [
        "営業収益",          # 0
        "売上原価",          # 1
        "売上総利益",        # 2
        "販管費",            # 3
        "営業利益",          # 4
        "営業外収益",        # 5
        "営業外費用",        # 6
        "経常利益",          # 7
        "法人税等",          # 8
        "当期純利益",        # 9
    ]

    node_colors = [
        COLORS["revenue"],   # 営業収益
        COLORS["cost"],      # 売上原価
        COLORS["subtotal"],  # 売上総利益
        COLORS["expense"],   # 販管費
        COLORS["profit"],    # 営業利益
        COLORS["positive"],  # 営業外収益
        COLORS["negative"],  # 営業外費用
        COLORS["profit"],    # 経常利益
        COLORS["tax"],       # 法人税等
        COLORS["profit"],    # 当期純利益
    ]

    source = [0, 0, 2, 2, 4, 5, 4, 7, 7]
    target = [1, 2, 3, 4, 7, 7, 6, 8, 9]
    values = [
        row["売上原価"],
        row["売上総利益"],
        row["販管費"],
        row["営業利益"],
        row["営業利益"],
        row["営業外収益"],
        row["営業外費用"],
        row["法人税等"],
        row["当期純利益"],
    ]

    # 負の値をゼロにクランプ
    values = [max(0, v) for v in values]

    link_colors = [
        "rgba(255,87,34,0.3)",   # 原価
        "rgba(66,165,245,0.3)",  # 売上総利益
        "rgba(255,152,0,0.3)",   # 販管費
        "rgba(76,175,80,0.3)",   # 営業利益
        "rgba(76,175,80,0.3)",   # 営業利益→経常利益
        "rgba(76,175,80,0.2)",   # 営業外収益
        "rgba(255,87,34,0.2)",   # 営業外費用
        "rgba(156,39,176,0.3)",  # 法人税等
        "rgba(76,175,80,0.3)",   # 純利益
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            label=[f"{l}<br>{int(row.get(l, 0)):,}" if l in row.index else l
                   for l in labels],
            color=node_colors,
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>%{value:,} 百万円<extra></extra>",
        ),
    )])

    fig.update_layout(
        title=dict(text=f"損益計算書フロー ({period_label})", font=dict(size=16)),
        font=dict(size=11),
        height=700,
        margin=dict(l=30, r=150, t=50, b=40),
    )
    fig.update_traces(node=dict(pad=25))
    return fig


def create_waterfall(
    categories: list[str],
    values: list[float],
    title: str,
    measures: list[str] | None = None,
    unit: str = "百万円",
    hover_texts: list[str] | None = None,
) -> go.Figure:
    """ウォーターフォールチャートを生成する。

    Args:
        categories: カテゴリラベルのリスト。
        values: 各カテゴリの値。
        title: チャートタイトル。
        measures: 各バーの種類（"relative", "total", "absolute"）。
        unit: 値の単位。
        hover_texts: 各バーのホバー時に表示する説明テキスト。

    Returns:
        Plotly Figure。
    """
    if measures is None:
        measures = ["absolute"] + ["relative"] * (len(categories) - 2) + ["total"]

    colors_increasing = COLORS["positive"]
    colors_decreasing = COLORS["negative"]
    colors_total = COLORS["total"]

    waterfall_kwargs: dict[str, Any] = dict(
        orientation="v",
        measure=measures,
        x=categories,
        y=values,
        text=[f"{v:+,.0f}" if m == "relative" else f"{v:,.0f}"
              for v, m in zip(values, measures)],
        textposition="outside",
        increasing=dict(marker=dict(color=colors_increasing)),
        decreasing=dict(marker=dict(color=colors_decreasing)),
        totals=dict(marker=dict(color=colors_total)),
        connector=dict(line=dict(color="rgba(0,0,0,0.3)", width=1)),
    )

    if hover_texts is not None:
        waterfall_kwargs["hovertext"] = hover_texts
        waterfall_kwargs["hovertemplate"] = (
            "<b>%{x}</b><br>%{hovertext}<br>金額: %{y:,.0f} " + unit + "<extra></extra>"
        )
    else:
        waterfall_kwargs["hovertemplate"] = "%{x}<br>%{y:,.0f} " + unit + "<extra></extra>"

    fig = go.Figure(go.Waterfall(**waterfall_kwargs))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        yaxis_title=unit,
        height=450,
        margin=dict(l=60, r=20, t=50, b=80),
        showlegend=False,
    )
    return fig


def create_treemap(
    labels: list[str],
    parents: list[str],
    values: list[float],
    title: str,
    color_values: list[float] | None = None,
) -> go.Figure:
    """ツリーマップを生成する。

    Args:
        labels: ノードラベル。
        parents: 親ノード名。
        values: 各ノードのサイズ値。
        title: チャートタイトル。
        color_values: 色付け用の値（前年比率など）。

    Returns:
        Plotly Figure。
    """
    marker: dict[str, Any] = {}
    if color_values is not None:
        marker = dict(
            colors=color_values,
            colorscale="RdYlGn",
            cmid=0,
            colorbar=dict(title="前年比(%)"),
        )

    treemap_kwargs: dict[str, Any] = dict(
        labels=labels,
        parents=parents,
        values=values,
        marker=marker,
        hovertemplate="<b>%{label}</b><br>売上: %{value:,} 百万円<br>構成比: %{percentParent:.1%}<extra></extra>",
    )

    if color_values is not None:
        # 前年比を直接ブロック内に表示
        treemap_kwargs["customdata"] = color_values
        treemap_kwargs["texttemplate"] = (
            "<b>%{label}</b><br>%{value:,} 百万円<br>前年比: %{customdata:+.1f}%"
        )
        treemap_kwargs["hovertemplate"] = (
            "<b>%{label}</b><br>売上: %{value:,} 百万円<br>"
            "構成比: %{percentParent:.1%}<br>前年比: %{customdata:+.1f}%<extra></extra>"
        )
    else:
        treemap_kwargs["textinfo"] = "label+value+percent parent"

    fig = go.Figure(go.Treemap(**treemap_kwargs))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        height=450,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def create_bs_block(row: pd.Series, period_label: str) -> go.Figure:
    """B/Sブロック図（横棒積み上げ）を生成する。

    Args:
        row: B/Sの1期分のデータ行。
        period_label: 表示用期間ラベル。

    Returns:
        Plotly Figure。
    """
    fig = go.Figure()

    # 資産側（左）
    asset_items = [
        ("現金及び預金", row["現金及び預金"], "#64B5F6"),
        ("売掛金", row["売掛金"], "#90CAF9"),
        ("その他流動資産", row["その他流動資産"], "#BBDEFB"),
        ("有形固定資産", row["有形固定資産"], "#1565C0"),
        ("無形固定資産", row["無形固定資産"], "#1976D2"),
        ("投資その他", row["投資その他"], "#1E88E5"),
    ]

    # 負債・純資産側（右）
    le_items = [
        ("買掛金", row["買掛金"], "#EF9A9A"),
        ("その他流動負債", row["その他流動負債"], "#E57373"),
        ("長期借入金", row["長期借入金"], "#EF5350"),
        ("その他固定負債", row["その他固定負債"], "#F44336"),
        ("資本金", row["資本金"], "#A5D6A7"),
        ("資本剰余金", row["資本剰余金"], "#81C784"),
        ("利益剰余金", row["利益剰余金"], "#66BB6A"),
    ]

    categories = ["資産", "負債・純資産"]

    for name, val, color in asset_items:
        fig.add_trace(go.Bar(
            name=name,
            x=[val, 0],
            y=categories,
            orientation="h",
            marker_color=color,
            text=[f"{name}<br>{int(val):,}", ""],
            textposition="inside",
            hovertemplate=f"{name}: {int(val):,} 百万円<extra></extra>",
        ))

    total_le = sum(v for _, v, _ in le_items)
    for name, val, color in le_items:
        pct = val / total_le * 100 if total_le else 0
        # 構成比が小さい項目はラベルを短縮
        if pct < 5:
            label = f"{int(val):,}"
        else:
            label = f"{name}<br>{int(val):,}"
        fig.add_trace(go.Bar(
            name=name,
            x=[0, val],
            y=categories,
            orientation="h",
            marker_color=color,
            text=["", label],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=f"<b>{name}</b>: {int(val):,} 百万円 ({pct:.1f}%)<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=dict(text=f"貸借対照表 ({period_label})", font=dict(size=16)),
        height=350,
        xaxis_title="百万円",
        margin=dict(l=110, r=20, t=50, b=40),
        showlegend=False,
        uniformtext=dict(minsize=8, mode="hide"),
    )
    return fig


def create_cf_sankey(row: pd.Series, period_label: str) -> go.Figure:
    """CFサンキーダイアグラムを生成する。

    Args:
        row: CFの1期分のデータ行。
        period_label: 表示用期間ラベル。

    Returns:
        Plotly Figure。
    """
    labels = [
        f"期首現金<br>{int(row['期首現金']):,}",   # 0
        f"営業CF<br>{int(row['営業CF']):+,}",       # 1
        f"投資CF<br>{int(row['投資CF']):+,}",       # 2
        f"財務CF<br>{int(row['財務CF']):+,}",       # 3
        f"期末現金<br>{int(row['期末現金']):,}",     # 4
    ]

    node_colors = [
        COLORS["total"],
        COLORS["operating_cf"],
        COLORS["investing_cf"],
        COLORS["financing_cf"],
        COLORS["total"],
    ]

    source: list[int] = []
    target: list[int] = []
    values: list[float] = []
    link_colors: list[str] = []

    # 期首現金 → 期末現金（ベースフロー）
    source.append(0)
    target.append(4)
    values.append(row["期首現金"])
    link_colors.append("rgba(33,150,243,0.2)")

    # 営業CF（通常プラス）
    if row["営業CF"] > 0:
        source.append(1)
        target.append(4)
        values.append(row["営業CF"])
        link_colors.append("rgba(76,175,80,0.4)")

    # 投資CF（通常マイナス＝流出）
    if row["投資CF"] < 0:
        source.append(0)
        target.append(2)
        values.append(abs(row["投資CF"]))
        link_colors.append("rgba(255,152,0,0.4)")

    # 財務CF
    if row["財務CF"] < 0:
        source.append(0)
        target.append(3)
        values.append(abs(row["財務CF"]))
        link_colors.append("rgba(156,39,176,0.4)")
    elif row["財務CF"] > 0:
        source.append(3)
        target.append(4)
        values.append(row["財務CF"])
        link_colors.append("rgba(156,39,176,0.4)")

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>%{value:,} 百万円<extra></extra>",
        ),
    )])

    fig.update_layout(
        title=dict(text=f"キャッシュフロー ({period_label})", font=dict(size=16)),
        font=dict(size=12),
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def create_trend_chart(
    df: pd.DataFrame,
    columns: list[str],
    title: str,
    unit: str = "百万円",
) -> go.Figure:
    """時系列推移チャートを生成する。

    Args:
        df: 期列を含む DataFrame。
        columns: プロットする列名リスト。
        title: チャートタイトル。
        unit: 値の単位。

    Returns:
        Plotly Figure。
    """
    palette = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336", "#00BCD4"]
    fig = go.Figure()

    period_labels = [str(p) for p in df["期"]]

    for i, col in enumerate(columns):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=period_labels,
            y=df[col],
            mode="lines+markers+text",
            name=col,
            line=dict(color=color, width=2),
            marker=dict(size=8),
            text=[f"{int(v):,}" for v in df[col]],
            textposition="top center",
            textfont=dict(size=10),
            hovertemplate=f"{col}: %{{y:,.0f}} {unit}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        yaxis_title=unit,
        height=400,
        margin=dict(l=60, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def create_gauge(value: float, title: str, suffix: str = "%",
                 ranges: list[tuple[float, float, str]] | None = None) -> go.Figure:
    """ゲージチャートを生成する。

    Args:
        value: 表示する値。
        title: 指標名。
        suffix: 値の接尾辞。
        ranges: (min, max, color) のリスト。

    Returns:
        Plotly Figure。
    """
    if ranges is None:
        ranges = [(0, 10, "#FF5722"), (10, 20, "#FF9800"), (20, 50, "#4CAF50")]

    steps = [dict(range=[r[0], r[1]], color=r[2]) for r in ranges]
    max_val = max(r[1] for r in ranges)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=suffix, font=dict(size=24)),
        title=dict(text=title, font=dict(size=14)),
        gauge=dict(
            axis=dict(range=[0, max_val]),
            bar=dict(color="#1565C0"),
            steps=steps,
            threshold=dict(
                line=dict(color="red", width=2),
                thickness=0.75,
                value=value,
            ),
        ),
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=50, b=10),
    )
    return fig
