import pandas as pd
import os


def build_volatility_factor(raw_data: pd.DataFrame, window: int = 10) -> pd.Series:
    """
    Oil Price Volatility Factor

    Parameters
    ----------
    raw_data : pd.DataFrame
        Must contain columns 'Date' and 'Price'.
    window : int
        Rolling window in days for standard deviation calculation.

    Returns
    -------
    pd.Series
        DatetimeIndex, name = 'diesel_price_volatility_factor_v1'
    """
    df = raw_data.copy()

    # 转换日期
    df['Date'] = pd.to_datetime(df['Date'])

    # 排序
    df = df.sort_values('Date')

    # 计算滚动标准差（波动率）
    df['volatility'] = df['Price'].rolling(window=window).std()

    factor = df.set_index('Date')['volatility']
    factor.name = 'diesel_price_volatility_factor_v1'

    return factor


if __name__ == "__main__":
    print("Start building Diesel Price Volatility Factor")

    # 当前脚本路径
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Excel 数据路径（改成你的文件名）
    excel_path = os.path.join(base_dir, "USA Daily Diesel Spot Price.xlsx")

    # 输出 CSV 路径
    output_csv = os.path.join(base_dir, "diesel_price_volatility_factor_v1.csv")

    # 读取数据
    raw_df = pd.read_excel(excel_path)

    # 构建因子（滚动窗口可自定义）
    factor_series = build_volatility_factor(raw_df, window=10)

    # 输出 CSV
    factor_df = factor_series.reset_index()
    factor_df.columns = ['Date', factor_series.name]
    factor_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("Factor build finished")
    print(f"CSV saved to: {output_csv}")
    print("\nPreview:")
    print(factor_df.head(15))
