# -*- coding: utf-8 -*-
"""
主流程：依次执行 1 相关性分析 -> 2 聚类去重 -> 3 因子过滤
在「相关性分析和去重」目录下运行：python run_pipeline.py
"""
import os
import sys
import subprocess
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(name):
    """在 SCRIPT_DIR 下执行指定脚本。"""
    path = os.path.join(SCRIPT_DIR, name)
    subprocess.run([sys.executable, path], cwd=SCRIPT_DIR, check=True)


def main():
    print("===== 1. 相关性分析 =====")
    run_script("1_correlation_analysis.py")

    print("\n===== 2. 因子聚类与去重 =====")
    run_script("2_factor_clustering_dedup.py")

    print("\n===== 3. 因子过滤（剔除较差因子）=====")
    run_script("3_factor_filter.py")

    # 读取最终结果简要汇总
    from config import OUTPUT_DIR, OUTPUT_FILTERED_LIST, OUTPUT_REMOVED_LIST
    path_ok = os.path.join(OUTPUT_DIR, OUTPUT_FILTERED_LIST)
    path_rm = os.path.join(OUTPUT_DIR, OUTPUT_REMOVED_LIST)
    n_ok = len(pd.read_csv(path_ok)) if os.path.isfile(path_ok) else 0
    n_rm = len(pd.read_csv(path_rm)) if os.path.isfile(path_rm) else 0
    print("\n===== 完成 =====")
    print(f"最终保留因子数: {n_ok}")
    print(f"被剔除因子数: {n_rm}")
    print(f"结果目录: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
