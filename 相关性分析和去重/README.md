# 因子相关性分析与去重

对 `ULTIMATE_OIL_PRICE_DATASET.csv` 中的因子做相关性分析、聚类去重和质量过滤，得到最终保留因子列表。

## 环境

手动安装依赖后运行  
```bash
pip install -r requirements.txt
python run_pipeline.py
```

若只想检查环境、不运行流程，可执行：  
```bash
python check_env.py
```

## 一键运行

在**本目录**下执行：

```bash
python run_pipeline.py
```

将依次执行：**1 相关性分析 → 2 聚类去重 → 3 因子过滤**，结果输出到 `output/`。**所有可视化图表**统一输出到 **`output/figures/`** 文件夹。

## 可视化输出（output/figures/）

| 内容 | 说明 |
|------|------|
| **figures/** | 可视化专用文件夹（与 CSV 同级的 output 下） |
| **all_pairwise_pearson.csv** | 每两个因子之间的 Pearson 相关系数表（factor_a, factor_b, pearson_r） |
| **correlation_heatmap.png** | 因子间相关矩阵热力图 |
| **missing_ratio_bar.png** | 各因子缺失率条形图 |
| **top_pairs_pearson_bar.png** | 相关系数绝对值最高的前 20 对因子条形图 |
| **pair_scatter/** | 高相关因子对的散点图（前 12 对，每对一张图） |
| **cluster_dendrogram.png** | 因子层次聚类树状图 |

## 分步运行

1. **1_correlation_analysis.py**  
   计算因子间 Pearson 相关矩阵、缺失率、基本统计；若存在 `数据集/DCOILWTICO.csv`，会计算因子与油价收益率的相关系数（IC）。  
   输出：`output/*.csv`、**`output/figures/`**（每对 Pearson 表、热力图、缺失率图、Top 对条形图、高相关对散点图）。

2. **2_factor_clustering_dedup.py**  
   基于相关矩阵做高相关去重：两因子相关系数绝对值 > 阈值（默认 0.85）时保留其一（按有效观测数多的保留）。并生成层次聚类树状图。  
   输出：`output/factor_clusters.csv`、`output/high_corr_pairs.csv`、**`output/figures/cluster_dendrogram.png`**。

3. **3_factor_filter.py**  
   对去重后保留的因子做质量过滤：有效观测占比过低、方差为 0/NaN 的剔除；若存在目标 IC 文件，可剔除与目标相关性过弱的因子。  
   输出：`output/filtered_factors.csv`（最终保留）、`output/removed_factors.csv`（被剔除及原因）。

## 配置

在 `config.py` 中可修改：

- **FACTOR_CSV**：主因子数据集路径  
- **CORR_DEDUP_THRESHOLD**：高相关去重阈值（默认 0.85）  
- **MIN_VALID_RATIO**：有效观测占比下限（默认 0.30）  
- **MIN_TARGET_IC_ABS**：与目标 |IC| 下限（默认 0.01，仅在提供油价时生效）  
- **FIGURES_DIR**：可视化子文件夹名（默认 `figures`）  
- **TOP_N_PAIRS_BAR**：条形图显示前 N 对（默认 20）  
- **TOP_N_PAIRS_SCATTER**：为前 N 对高相关画散点图（默认 12）

## 输出说明

| 文件 | 说明 |
|------|------|
| `filtered_factors.csv` | 最终保留的因子列表，供下游建模使用 |
| `removed_factors.csv` | 被剔除的因子及剔除原因 |
| `factor_correlation_matrix.csv` | 因子间相关矩阵 |
| `factor_missing_stats.csv` | 各因子缺失率、有效观测数 |
| `factor_clusters.csv` | 去重后每个因子的保留/剔除状态 |
| `high_corr_pairs.csv` | 高相关因子对及相关系数 |
| **figures/all_pairwise_pearson.csv** | 每两个因子的 Pearson 相关系数（全表） |
| **figures/** 下 PNG | 热力图、缺失率图、Top 对条形图、散点图、聚类树状图 |
