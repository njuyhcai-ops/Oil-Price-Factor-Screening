# -*- coding: utf-8 -*-
"""
3. 因子过滤（剔除较差因子）
- 有效观测占比低于阈值的剔除（缺失过多）
- 近常数因子剔除（取值几乎不变）
- 方差极低（信息量极低）可标记或剔除
- 若提供目标 IC：与目标 |IC| 过低的剔除（可选）
- 结合去重结果：只对「去重后保留」的因子做上述过滤，得到最终保留列表
"""
import os
import pandas as pd
import numpy as np
from config import (
    OUTPUT_DIR,
    OUTPUT_MISSING_STATS,
    OUTPUT_FACTOR_STATS,
    OUTPUT_CLUSTER_RESULT,
    OUTPUT_FILTERED_LIST,
    OUTPUT_REMOVED_LIST,
    MIN_VALID_RATIO,
    MAX_CONSTANT_RATIO,
    LOW_VARIANCE_PERCENTILE,
    MIN_TARGET_IC_ABS,
)


def load_inputs(output_dir=None):
    """加载缺失统计、基本统计、去重结果、可选目标 IC。"""
    output_dir = output_dir or OUTPUT_DIR
    path_miss = os.path.join(output_dir, OUTPUT_MISSING_STATS)
    path_stats = os.path.join(output_dir, OUTPUT_FACTOR_STATS)
    path_cluster = os.path.join(output_dir, OUTPUT_CLUSTER_RESULT)
    path_ic = os.path.join(output_dir, "factor_target_ic.csv")

    if not os.path.isfile(path_miss):
        raise FileNotFoundError(f"请先运行 1_correlation_analysis.py: {path_miss}")
    if not os.path.isfile(path_cluster):
        raise FileNotFoundError(f"请先运行 2_factor_clustering_dedup.py: {path_cluster}")

    missing = pd.read_csv(path_miss)
    cluster = pd.read_csv(path_cluster)
    stats = pd.read_csv(path_stats) if os.path.isfile(path_stats) else None
    target_ic = None
    if os.path.isfile(path_ic):
        ic_df = pd.read_csv(path_ic, index_col=0)
        if ic_df.shape[0] > 0:
            target_ic = ic_df.iloc[:, 0] if ic_df.shape[1] >= 1 else None

    # 去重后保留的因子
    kept_from_dedup = cluster[cluster["dedup_status"] == "kept"]["factor"].tolist()
    return missing, stats, kept_from_dedup, target_ic


def filter_factors(missing_df, stats_df, kept_from_dedup, target_ic=None):
    """
    对 kept_from_dedup 中的因子做质量过滤。
    返回：最终保留列表、被剔除列表及原因。
    """
    # 只考虑去重后保留的因子
    candidates = set(kept_from_dedup)
    missing = missing_df[missing_df["factor"].isin(candidates)].set_index("factor")
    if stats_df is not None:
        stats = stats_df[stats_df["factor"].isin(candidates)].set_index("factor")
    else:
        stats = None

    removed_reasons = []
    still_ok = set(candidates)

    # 1) 有效观测占比
    for f in list(still_ok):
        if f not in missing.index:
            continue
        valid_ratio = missing.loc[f, "valid_ratio"]
        if valid_ratio < MIN_VALID_RATIO:
            still_ok.discard(f)
            removed_reasons.append({"factor": f, "reason": f"low_valid_ratio ({valid_ratio:.2%} < {MIN_VALID_RATIO:.0%})"})

    # 2) 近常数：方差为 0 或 NaN 的剔除（低方差百分位仅作参考，不自动剔除）
    if stats is not None and "variance" in stats.columns:
        var_series = stats.loc[stats.index.intersection(still_ok), "variance"]
        for f in list(still_ok):
            if f not in var_series.index:
                continue
            v = var_series[f]
            if pd.isna(v) or v <= 0:
                still_ok.discard(f)
                removed_reasons.append({"factor": f, "reason": "zero_or_nan_variance"})

    # 3) 与目标 IC 过弱（可选）
    if target_ic is not None and len(target_ic) > 0:
        for f in list(still_ok):
            if f not in target_ic.index:
                continue
            ic = target_ic[f]
            if pd.isna(ic) or abs(ic) < MIN_TARGET_IC_ABS:
                still_ok.discard(f)
                removed_reasons.append({"factor": f, "reason": f"low_target_ic (|IC|={ic:.4f} < {MIN_TARGET_IC_ABS})"})

    filtered = sorted(still_ok)
    removed = sorted(candidates - still_ok)
    reasons_df = pd.DataFrame(removed_reasons) if removed_reasons else pd.DataFrame(columns=["factor", "reason"])
    return filtered, removed, reasons_df


def run(output_dir=None):
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    missing, stats, kept_from_dedup, target_ic = load_inputs(output_dir)
    filtered, removed, reasons_df = filter_factors(missing, stats, kept_from_dedup, target_ic)

    # 保存最终保留因子列表
    path_filtered = os.path.join(output_dir, OUTPUT_FILTERED_LIST)
    pd.DataFrame({"factor": filtered}).to_csv(path_filtered, index=False, encoding="utf-8-sig")
    print(f"最终保留因子已保存: {path_filtered}，共 {len(filtered)} 个")

    # 被剔除因子及原因
    path_removed = os.path.join(output_dir, OUTPUT_REMOVED_LIST)
    if len(removed) > 0:
        removed_df = pd.DataFrame({"factor": removed}).merge(reasons_df, on="factor", how="left")
        removed_df.to_csv(path_removed, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(columns=["factor", "reason"]).to_csv(path_removed, index=False, encoding="utf-8-sig")
    print(f"被剔除因子已保存: {path_removed}，共 {len(removed)} 个")

    return {"filtered": filtered, "removed": removed, "reasons_df": reasons_df}


if __name__ == "__main__":
    run()
