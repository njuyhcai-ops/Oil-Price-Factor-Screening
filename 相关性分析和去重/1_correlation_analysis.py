# -*- coding: utf-8 -*-
"""
1. 因子相关性分析
- 计算因子间 Pearson 相关矩阵
- 计算各因子缺失率、有效观测数
- 基本统计：均值、标准差、方差
- 可选：与目标（油价收益率）的相关系数
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import (
    PROJECT_ROOT,
    FACTOR_CSV,
    OIL_PRICE_CSV,
    OIL_PRICE_DATE_COL,
    OIL_PRICE_VALUE_COL,
    OUTPUT_DIR,
    OUTPUT_CORR_MATRIX,
    OUTPUT_MISSING_STATS,
    OUTPUT_FACTOR_STATS,
    FIGURES_DIR,
    FIG_DPI,
    FIG_CORR_HEATMAP,
    FIG_MISSING_BAR,
    FIG_TOP_PAIRS_BAR,
    PAIR_SCATTER_DIR,
    TOP_N_PAIRS_SCATTER,
    TOP_N_PAIRS_BAR,
    OUTPUT_PAIRWISE_PEARSON,
)


def load_factor_data():
    """加载因子数据，返回 DataFrame 与因子列名列表。"""
    df = pd.read_csv(FACTOR_CSV)
    df["Date"] = pd.to_datetime(df["Date"])
    factor_cols = [c for c in df.columns if c != "Date"]
    return df, factor_cols


def correlation_matrix(df, factor_cols):
    """计算因子间 Pearson 相关矩阵（仅用有效值）。"""
    sub = df[factor_cols]
    corr = sub.corr(method="pearson")
    return corr


def missing_stats(df, factor_cols):
    """各因子缺失率与有效观测数。"""
    n = len(df)
    rows = []
    for c in factor_cols:
        valid = df[c].notna().sum()
        missing = df[c].isna().sum()
        rows.append({
            "factor": c,
            "valid_count": int(valid),
            "missing_count": int(missing),
            "valid_ratio": round(valid / n, 4),
            "missing_ratio": round(missing / n, 4),
        })
    return pd.DataFrame(rows)


def basic_stats(df, factor_cols):
    """各因子基本统计：均值、标准差、方差、最小值、最大值。"""
    sub = df[factor_cols]
    stats = sub.describe().T[["mean", "std", "min", "max"]].copy()
    stats["variance"] = sub.var()
    stats.index.name = "factor"
    stats = stats.reset_index()
    return stats


def all_pairwise_pearson(corr):
    """将相关矩阵展开为每对因子的 Pearson 表：factor_a, factor_b, pearson_r（上三角，不含自身）。"""
    rows = []
    cols = corr.columns.tolist()
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            r = corr.loc[a, b]
            rows.append({"factor_a": a, "factor_b": b, "pearson_r": round(float(r), 6)})
    return pd.DataFrame(rows)


def target_correlation_if_available(df, factor_cols):
    """
    若存在油价数据，计算因子与「当期油价收益率」的相关系数（IC）。
    返回 Series: factor -> ic，若未提供油价则返回 None。
    """
    if not OIL_PRICE_CSV or not os.path.isfile(OIL_PRICE_CSV):
        return None
    try:
        oil = pd.read_csv(OIL_PRICE_CSV)
        oil[OIL_PRICE_DATE_COL] = pd.to_datetime(oil[OIL_PRICE_DATE_COL])
        oil = oil.rename(columns={OIL_PRICE_DATE_COL: "Date", OIL_PRICE_VALUE_COL: "price"})
        oil = oil[["Date", "price"]].dropna()
        oil = oil.sort_values("Date").drop_duplicates("Date")
        oil["ret"] = oil["price"].pct_change()
        oil = oil.dropna(subset=["ret"])
        merged = df[["Date"] + factor_cols].merge(oil[["Date", "ret"]], on="Date", how="inner")
        if len(merged) < 100:
            return None
        ics = {}
        for c in factor_cols:
            valid = merged[[c, "ret"]].dropna()
            if len(valid) < 100:
                ics[c] = np.nan
                continue
            ics[c] = valid[c].corr(valid["ret"])
        return pd.Series(ics)
    except Exception:
        return None


def run(output_dir=None):
    output_dir = output_dir or OUTPUT_DIR
    figures_dir = os.path.join(output_dir, FIGURES_DIR)
    pair_scatter_dir = os.path.join(figures_dir, PAIR_SCATTER_DIR)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(pair_scatter_dir, exist_ok=True)

    df, factor_cols = load_factor_data()
    print(f"因子数量: {len(factor_cols)}, 样本数: {len(df)}")

    # 1) 相关矩阵
    corr = correlation_matrix(df, factor_cols)
    path_corr = os.path.join(output_dir, OUTPUT_CORR_MATRIX)
    corr.to_csv(path_corr, encoding="utf-8-sig")
    print(f"相关矩阵已保存: {path_corr}")

    # 2) 缺失统计
    miss = missing_stats(df, factor_cols)
    path_miss = os.path.join(output_dir, OUTPUT_MISSING_STATS)
    miss.to_csv(path_miss, index=False, encoding="utf-8-sig")
    print(f"缺失统计已保存: {path_miss}")

    # 3) 基本统计
    stats = basic_stats(df, factor_cols)
    path_stats = os.path.join(output_dir, OUTPUT_FACTOR_STATS)
    stats.to_csv(path_stats, index=False, encoding="utf-8-sig")
    print(f"基本统计已保存: {path_stats}")

    # 4) 与目标相关性（可选）
    target_ic = target_correlation_if_available(df, factor_cols)
    if target_ic is not None:
        path_ic = os.path.join(output_dir, "factor_target_ic.csv")
        target_ic.to_csv(path_ic, encoding="utf-8-sig")
        print(f"因子-目标IC已保存: {path_ic}")

    # 5) 每两个因子的 Pearson 相关系数表 -> 输出到 figures 文件夹
    pairwise_df = all_pairwise_pearson(corr)
    pairwise_df["abs_pearson_r"] = pairwise_df["pearson_r"].abs()
    path_pairwise = os.path.join(figures_dir, OUTPUT_PAIRWISE_PEARSON)
    pairwise_df.to_csv(path_pairwise, index=False, encoding="utf-8-sig")
    print(f"每对因子 Pearson 表已保存: {path_pairwise}")

    # 6) 可视化：统一保存到 output/figures/
    try:
        import matplotlib
        matplotlib.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False
        import seaborn as sns
        # 6.1 相关矩阵热力图
        fig, ax = plt.subplots(figsize=(14, 12))
        sns.heatmap(corr, ax=ax, cmap="RdBu_r", center=0, vmin=-1, vmax=1)
        ax.set_title("Factor Correlation Matrix (Pearson)")
        fig.savefig(os.path.join(figures_dir, FIG_CORR_HEATMAP), dpi=FIG_DPI, bbox_inches="tight")
        plt.close()
        print(f"相关热力图已保存: {figures_dir}/{FIG_CORR_HEATMAP}")
    except Exception as e:
        print("热力图跳过:", e)

    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        miss_sorted = miss.sort_values("missing_ratio", ascending=False)
        ax.barh(range(len(miss_sorted)), miss_sorted["missing_ratio"].values)
        ax.set_yticks(range(len(miss_sorted)))
        ax.set_yticklabels(miss_sorted["factor"].values, fontsize=8)
        ax.set_xlabel("Missing Ratio")
        ax.set_title("Factor Missing Ratio")
        fig.savefig(os.path.join(figures_dir, FIG_MISSING_BAR), dpi=FIG_DPI, bbox_inches="tight")
        plt.close()
        print(f"缺失率条形图已保存: {figures_dir}/{FIG_MISSING_BAR}")
    except Exception as e:
        print("缺失率图跳过:", e)

    # 6.2 相关系数绝对值最高的前 N 对（条形图）
    try:
        top_pairs = pairwise_df.nlargest(TOP_N_PAIRS_BAR, "abs_pearson_r")
        top_pairs = top_pairs.sort_values("abs_pearson_r", ascending=True)
        labels = [f"{row['factor_a'][:15]} vs {row['factor_b'][:15]}" for _, row in top_pairs.iterrows()]
        fig, ax = plt.subplots(figsize=(10, max(6, len(top_pairs) * 0.25)))
        ax.barh(range(len(top_pairs)), top_pairs["pearson_r"].values, color="steelblue", alpha=0.8)
        ax.set_yticks(range(len(top_pairs)))
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel("Pearson r")
        ax.set_title(f"Top {TOP_N_PAIRS_BAR} Factor Pairs by |Pearson|")
        ax.axvline(0, color="gray", linewidth=0.5)
        fig.savefig(os.path.join(figures_dir, FIG_TOP_PAIRS_BAR), dpi=FIG_DPI, bbox_inches="tight")
        plt.close()
        print(f"Top 因子对条形图已保存: {figures_dir}/{FIG_TOP_PAIRS_BAR}")
    except Exception as e:
        print("Top 因子对条形图跳过:", e)

    # 6.3 高相关因子对散点图（前 N 对）
    try:
        def _safe_name(s, max_len=25):
            for c in r'/\:*?"<>|':
                s = s.replace(c, "_")
            return s[:max_len] if len(s) > max_len else s

        sub = df[factor_cols]
        top_for_scatter = pairwise_df.nlargest(TOP_N_PAIRS_SCATTER, "abs_pearson_r")
        n_saved = 0
        for i, row in enumerate(top_for_scatter.itertuples(index=False)):
            a, b, r = row.factor_a, row.factor_b, row.pearson_r
            valid = sub[[a, b]].dropna()
            if len(valid) < 50:
                continue
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.scatter(valid[a], valid[b], alpha=0.3, s=10)
            ax.set_xlabel(a[:30] + ("..." if len(a) > 30 else ""))
            ax.set_ylabel(b[:30] + ("..." if len(b) > 30 else ""))
            ax.set_title(f"Pearson r = {r:.4f}")
            fname = f"scatter_{i+1:02d}_{_safe_name(a)}_vs_{_safe_name(b)}.png"
            fig.savefig(os.path.join(pair_scatter_dir, fname), dpi=FIG_DPI, bbox_inches="tight")
            plt.close()
            n_saved += 1
        print(f"高相关对散点图已保存: {pair_scatter_dir}/ 共 {n_saved} 张")
    except Exception as e:
        print("散点图跳过:", e)

    print(f"所有可视化已输出到文件夹: {os.path.abspath(figures_dir)}")
    return {"corr": corr, "missing": miss, "stats": stats, "target_ic": target_ic}


if __name__ == "__main__":
    run()
