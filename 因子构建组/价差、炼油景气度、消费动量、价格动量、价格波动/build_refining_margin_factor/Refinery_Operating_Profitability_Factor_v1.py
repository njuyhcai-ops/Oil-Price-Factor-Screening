import pandas as pd
import os

def build_refinery_factor(raw_data: pd.DataFrame, config=None) -> pd.Series:
    """
    Refinery Operating Profitability Factor (炼厂景气度因子)

    Parameters
    ----------
    raw_data : pd.DataFrame
        原始数据表，包含列：Year, Quarter, Indicator, Value
    config : dict, optional
        - "lag": 滞后期数（季度），默认 1

    Returns
    -------
    factor : pd.Series
        - DatetimeIndex (季度末)
        - name = "Refinery_Operating_Profitability_Factor_v1"
    """
    if config is None:
        config = {"lag": 1}

    year_col = "Year"
    quarter_col = "Quarter"
    indicator_col = "Indicator"
    value_col = "Value"

    df = raw_data.copy()
    df[year_col] = df[year_col].astype(int)
    df[quarter_col] = df[quarter_col].astype(int)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # -------- 提取有效炼厂 --------
    refinery_names = ["USGC", "NWE", "Singapore"]
    df = df[df[indicator_col].str.contains("|".join(refinery_names), case=False, na=False)]

    # -------- 构建透视表，每列一个炼厂 --------
    pivot_df = df.pivot_table(
        index=[year_col, quarter_col],
        columns=indicator_col,
        values=value_col,
        aggfunc="mean"
    )

    # -------- 计算综合景气度（均值） --------
    pivot_df["Refinery_Operating_Profitability_Factor_v1"] = pivot_df.mean(axis=1)

    # -------- 构造季度末日期 --------
    quarter_end_month = {1: 3, 2: 6, 3: 9, 4: 12}
    pivot_df = pivot_df.reset_index()
    pivot_df["month"] = pivot_df[quarter_col].map(quarter_end_month)
    pivot_df["date"] = pd.to_datetime(
        dict(year=pivot_df[year_col], month=pivot_df["month"], day=1)
    ) + pd.offsets.MonthEnd(0)

    pivot_df = pivot_df.sort_values("date")

    # -------- 滞后处理 --------
    lag = config.get("lag", 1)
    pivot_df["Refinery_Operating_Profitability_Factor_v1"] = pivot_df["Refinery_Operating_Profitability_Factor_v1"].shift(lag)

    # -------- 输出 Series --------
    factor = pivot_df.set_index("date")["Refinery_Operating_Profitability_Factor_v1"]
    return factor


if __name__ == "__main__":
    print("Start building Refinery Operating Profitability Factor...")

    # 当前脚本路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "Oil Regional Refining Margins.xlsx")
    output_excel = os.path.join(base_dir, "Refinery_Operating_Profitability_Factor_v1.xlsx")

    # -------- 读取数据 --------
    raw_df = pd.read_excel(excel_path)

    # -------- 构建因子（可修改滞后期） --------
    factor_series = build_refinery_factor(raw_data=raw_df, config={"lag": 1})

    # -------- 输出 Excel --------
    factor_df = factor_series.reset_index()
    factor_df.columns = ["date", factor_series.name]
    factor_df.to_excel(output_excel, index=False)

    print("Factor build finished.")
    print(f"Excel saved to: {output_excel}")
    print("\nPreview:")
    print(factor_df.head())
