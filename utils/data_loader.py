"""CSVデータ読み込み・変換モジュール。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def list_companies() -> list[dict[str, str]]:
    """利用可能な企業一覧を返す。

    Returns:
        企業コードと名前の辞書リスト。
    """
    companies: list[dict[str, str]] = []
    for d in sorted(DATA_DIR.iterdir()):
        info_path = d / "company.json"
        if d.is_dir() and info_path.exists():
            info = json.loads(info_path.read_text(encoding="utf-8"))
            companies.append({"code": info["code"], "name": info["name"]})
    return companies


def load_company_info(code: str) -> dict[str, Any]:
    """企業基本情報を読み込む。

    Args:
        code: 証券コード。

    Returns:
        company.json の内容。
    """
    path = DATA_DIR / code / "company.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_pl(code: str) -> pd.DataFrame:
    """P/Lデータを読み込む。

    Args:
        code: 証券コード。

    Returns:
        損益計算書の DataFrame。
    """
    path = DATA_DIR / code / "pl.csv"
    return pd.read_csv(path, encoding="utf-8")


def load_bs(code: str) -> pd.DataFrame:
    """B/Sデータを読み込む。

    Args:
        code: 証券コード。

    Returns:
        貸借対照表の DataFrame。
    """
    path = DATA_DIR / code / "bs.csv"
    return pd.read_csv(path, encoding="utf-8")


def load_cf(code: str) -> pd.DataFrame:
    """CFデータを読み込む。

    Args:
        code: 証券コード。

    Returns:
        キャッシュフロー計算書の DataFrame。
    """
    path = DATA_DIR / code / "cf.csv"
    return pd.read_csv(path, encoding="utf-8")


def load_segment(code: str) -> pd.DataFrame:
    """セグメント別データを読み込む。

    Args:
        code: 証券コード。

    Returns:
        セグメント別の DataFrame。
    """
    path = DATA_DIR / code / "segment.csv"
    return pd.read_csv(path, encoding="utf-8")


def load_factors(code: str) -> pd.DataFrame:
    """変動要因データを読み込む。

    Args:
        code: 証券コード。

    Returns:
        変動要因の DataFrame。
    """
    path = DATA_DIR / code / "factors.csv"
    return pd.read_csv(path, encoding="utf-8")


def calc_yoy_change(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """前年比変化額・変化率を計算して列追加する。

    Args:
        df: 期列を含む DataFrame。
        col: 対象カラム名。

    Returns:
        {col}_前年比額 と {col}_前年比率 列を追加した DataFrame。
    """
    df = df.copy()
    df[f"{col}_前年比額"] = df[col].diff()
    df[f"{col}_前年比率"] = df[col].pct_change() * 100
    return df


def get_period_label(period: float | str) -> str:
    """期の値を表示用ラベルに変換する。

    Args:
        period: 期の値（例: 2024.12）。

    Returns:
        表示用ラベル（例: "2024年12月期"）。
    """
    s = str(period)
    if "." in s:
        year, month = s.split(".")
        return f"{year}年{month}月期"
    return f"{s}年12月期"
