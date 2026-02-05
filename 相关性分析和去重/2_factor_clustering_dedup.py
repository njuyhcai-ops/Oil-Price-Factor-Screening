# -*- coding: utf-8 -*-
"""
2. 因子聚类与去重
- 基于因子间相关矩阵做层次聚类（可选）
- 高相关因子对：|相关系数| > 阈值时保留其一（按有效观测数或方差优先保留）
- 输出：代表因子列表、聚类/分组结果
"""
import os
import pandas as pd
import numpy as np
from config import (
    OUTPUT_DIR,
    OUTPUT_CORR_MATRIX,
    OUTPUT_MISSING_STATS,
    OUTPUT_CLUSTER_RESULT,
    CORR_DEDUP_THRESHOLD,
    FIGURES_DIR,
    FIG_DPI,
    FIG_CLUSTER_DENDROGRAM,
)


def load_corr_and_missing(output_dir=None):
    """加载 1 步生成的相关矩阵与缺失统计。"""
    output_dir = output_dir or OUTPUT_DIR
    path_corr = os.path.join(output_dir, OUTPUT_CORR_MATRIX)
    path_miss = os.path.join(output_dir, OUTPUT_MISSING_STATS)
    if not os.path.isfile(path_corr):
        raise FileNotFoundError(f"请先运行 1_correlation_analysis.py 生成: {path_corr}")
    corr = pd.read_csv(path_corr, index_col=0)
    missing = pd.read_csv(path_miss) if os.path.isfile(path_miss) else None
    return corr, missing


def high_corr_pairs(corr, threshold):
    """找出所有 |相关系数| >= threshold 的因子对（不含自身，且每对只保留一次）。"""
    pairs = []
    cols = corr.columns.tolist()
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            r = corr.loc[a, b]
            if pd.isna(r):
                continue
            if abs(r) >= threshold:
                pairs.append((a, b, float(r)))
    return pairs


def greedy_dedup(corr, missing_df, threshold):
    """
    贪心去重：对高相关因子对，每次去掉「有效观测更少」或「方差更小」的一个，
    直到没有超过阈值的一对。
    返回：保留的因子列表、被剔除的因子列表。
    """
    factor_cols = corr.columns.tolist()
    keep = set(factor_cols)
    if missing_df is not None:
        valid_count = dict(zip(missing_df["factor"], missing_df["valid_count"]))
    else:
        valid_count = {f: 1 for f in factor_cols}

    pairs = high_corr_pairs(corr, threshold)
    # 按 |r| 从高到低处理，优先拆掉相关性最强的一对中的一个
    pairs.sort(key=lambda x: -abs(x[2]))

    for a, b, r in pairs:
        if a not in keep or b not in keep:
            continue
        # 保留有效观测更多的
        na, nb = valid_count.get(a, 0), valid_count.get(b, 0)
        if na >= nb:
            keep.discard(b)
        else:
            keep.discard(a)

    kept = sorted(keep)
    removed = sorted(set(factor_cols) - keep)
    return kept, removed


def clustering_from_corr(corr, method="average"):
    """
    基于 1 - |相关系数| 做层次聚类（距离越小越相似）。
    返回 linkage 矩阵，供画树状图。
    """
    from scipy.cluster.hierarchy import linkage
    dist = 1 - np.abs(corr.values)
    np.fill_diagonal(dist, 0)
    from scipy.spatial.distance import squareform
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method=method)
    return Z


def run(output_dir=None, threshold=None):
    output_dir = output_dir or OUTPUT_DIR
    threshold = threshold if threshold is not None else CORR_DEDUP_THRESHOLD
    os.makedirs(output_dir, exist_ok=True)

    corr, missing_df = load_corr_and_missing(output_dir)
    kept, removed = greedy_dedup(corr, missing_df, threshold)
    pairs = high_corr_pairs(corr, threshold)

    # 输出：代表因子列表、被剔除列表、高相关对
    result = []
    for f in corr.columns:
        status = "kept" if f in kept else "removed"
        result.append({"factor": f, "dedup_status": status})
    result_df = pd.DataFrame(result)
    path_result = os.path.join(output_dir, OUTPUT_CLUSTER_RESULT)
    result_df.to_csv(path_result, index=False, encoding="utf-8-sig")
    print(f"去重结果已保存: {path_result}")
    print(f"保留因子数: {len(kept)}, 剔除因子数: {len(removed)}")

    # 高相关对摘要
    pairs_df = pd.DataFrame(pairs, columns=["factor_a", "factor_b", "correlation"])
    path_pairs = os.path.join(output_dir, "high_corr_pairs.csv")
    pairs_df.to_csv(path_pairs, index=False, encoding="utf-8-sig")
    print(f"高相关对已保存: {path_pairs}")

    # 聚类树状图（可选）-> 保存到 output/figures/
    try:
        import matplotlib
        matplotlib.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False
        import matplotlib.pyplot as plt
        from scipy.cluster.hierarchy import dendrogram
        figures_dir = os.path.join(output_dir, FIGURES_DIR)
        os.makedirs(figures_dir, exist_ok=True)
        Z = clustering_from_corr(corr)
        fig, ax = plt.subplots(figsize=(14, 6))
        dendrogram(Z, labels=corr.columns.tolist(), ax=ax, leaf_rotation=90)
        ax.set_title("Factor Hierarchical Clustering (1 - |correlation|)")
        fig.savefig(os.path.join(figures_dir, FIG_CLUSTER_DENDROGRAM), dpi=FIG_DPI, bbox_inches="tight")
        plt.close()
        print(f"聚类树状图已保存: {figures_dir}/{FIG_CLUSTER_DENDROGRAM}")
    except Exception as e:
        print("聚类图跳过:", e)

    return {"kept": kept, "removed": removed, "pairs": pairs, "result_df": result_df}


if __name__ == "__main__":
    run()
