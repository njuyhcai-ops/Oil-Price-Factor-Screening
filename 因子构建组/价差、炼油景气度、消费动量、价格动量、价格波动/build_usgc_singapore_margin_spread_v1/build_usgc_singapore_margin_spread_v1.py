import pandas as pd
import os


def build_factor(df: pd.DataFrame, config: dict = None) -> pd.Series:
    if config is None:
        config = {'lag': 0, 'rolling_window': 1}
    lag = config.get('lag', 0)
    rolling_window = config.get('rolling_window', 1)

    # 修复浮点数年份和季度
    df['Year'] = df['Year'].fillna(0).astype(float).astype(int)
    df['Quarter'] = df['Quarter'].fillna(1).astype(float).astype(int)

    # 筛选指标
    usgc = df[df['Indicator'].str.contains('USGC', case=False, na=False)][['Year', 'Quarter', 'Value']].rename(
        columns={'Value': 'USGC'})
    singapore = df[df['Indicator'].str.contains('Singapore', case=False, na=False)][
        ['Year', 'Quarter', 'Value']].rename(columns={'Value': 'Singapore'})

    # 生成完整年份×季度表
    years = sorted(df['Year'].unique())
    quarters = [1, 2, 3, 4]
    all_quarters = pd.MultiIndex.from_product([years, quarters], names=['Year', 'Quarter']).to_frame(index=False)

    # 合并 USGC 和 Singapore 数据
    merged = all_quarters.merge(usgc, on=['Year', 'Quarter'], how='left').merge(singapore, on=['Year', 'Quarter'],
                                                                                how='left')

    # 计算价差
    merged['spread'] = merged['USGC'] - merged['Singapore']

    # 滞后 & 滚动
    merged['spread'] = merged['spread'].shift(lag)
    if rolling_window > 1:
        merged['spread'] = merged['spread'].rolling(window=rolling_window).mean()

    # 拼接季度末日期
    quarter_month = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}

    def safe_date(row):
        try:
            year = int(row['Year'])
            month_day = quarter_month.get(int(row['Quarter']), '03-31')
            return pd.Timestamp(f"{year}-{month_day}")
        except:
            return pd.NaT

    merged['date'] = merged.apply(safe_date, axis=1)

    # 输出 Series
    factor_series = pd.Series(data=merged['spread'].values, index=merged['date'])
    factor_series.name = 'usgc_singapore_margin_spread_factor_v1'
    return factor_series.dropna()


# ================== 主程序示例 ==================
if __name__ == "__main__":
    # 当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Excel 相对路径（假设在同一文件夹下）
    excel_path = os.path.join(script_dir, "Oil Regional Refining Margins.xlsx")

    # 输出 CSV 相对路径
    output_path = os.path.join(script_dir, "usgc_singapore_margin_spread_factor_v1.csv")

    # 读取 Excel
    raw_data = pd.read_excel(excel_path, usecols="A:D")

    # 构建因子
    factor_series = build_factor(raw_data, config={'lag': 1, 'rolling_window': 1})

    # 导出 CSV
    factor_series.reset_index().rename(columns={'index': 'date', factor_series.name: factor_series.name}).to_csv(
        output_path, index=False, encoding='utf-8-sig'
    )

    print("因子生成完成，前5行：")
    print(factor_series.head())
