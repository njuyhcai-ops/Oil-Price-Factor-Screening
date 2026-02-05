# -*- coding: utf-8 -*-
"""
相关性分析与去重 - 配置文件
"""
import os

# 项目根目录（因子组）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 主因子数据集路径
FACTOR_CSV = os.path.join(PROJECT_ROOT, "ULTIMATE_OIL_PRICE_DATASET.csv")

# 可选：油价序列路径（用于计算因子与目标的相关性，若不需要可设为 None）
OIL_PRICE_CSV = os.path.join(PROJECT_ROOT, "数据集", "DCOILWTICO.csv")
OIL_PRICE_DATE_COL = "observation_date"
OIL_PRICE_VALUE_COL = "DCOILWTICO"

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_CORR_MATRIX = "factor_correlation_matrix.csv"
OUTPUT_MISSING_STATS = "factor_missing_stats.csv"
OUTPUT_FACTOR_STATS = "factor_basic_stats.csv"
OUTPUT_CLUSTER_RESULT = "factor_clusters.csv"
OUTPUT_FILTERED_LIST = "filtered_factors.csv"
OUTPUT_REMOVED_LIST = "removed_factors.csv"

# 相关性去重阈值：两因子相关系数绝对值超过此值视为高度相关，保留其一
CORR_DEDUP_THRESHOLD = 0.85

# 因子过滤阈值
MIN_VALID_RATIO = 0.30          # 有效观测占比至少 30%（缺失率不高于 70%）
MAX_CONSTANT_RATIO = 0.99       # 若某因子 99% 以上为同一取值，视为近常数因子可剔除
LOW_VARIANCE_PERCENTILE = 5     # 方差处于最低 5% 的因子可标记为低信息量

# 与目标（油价收益率）相关性：若提供油价，可过滤与目标相关性极弱的因子（可选）
MIN_TARGET_IC_ABS = 0.01        # 与目标 |IC| 至少 0.01 才保留（若启用目标分析）

# 图表：统一输出到 output/figures/ 文件夹
FIGURES_DIR = "figures"  # 相对 OUTPUT_DIR 的可视化子文件夹
FIG_DPI = 150
FIG_CORR_HEATMAP = "correlation_heatmap.png"
FIG_MISSING_BAR = "missing_ratio_bar.png"
FIG_CLUSTER_DENDROGRAM = "cluster_dendrogram.png"
FIG_TOP_PAIRS_BAR = "top_pairs_pearson_bar.png"   # 相关系数绝对值最高的若干对
PAIR_SCATTER_DIR = "pair_scatter"                  # 因子对散点图子文件夹
TOP_N_PAIRS_SCATTER = 12                           # 为前 N 对高相关画散点图
TOP_N_PAIRS_BAR = 20                               # 条形图显示前 N 对
OUTPUT_PAIRWISE_PEARSON = "all_pairwise_pearson.csv"  # 每两个因子的 Pearson 表
