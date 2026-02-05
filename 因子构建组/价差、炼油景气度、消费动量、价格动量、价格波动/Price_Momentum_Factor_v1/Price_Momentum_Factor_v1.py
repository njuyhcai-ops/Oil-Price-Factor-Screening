import pandas as pd
import os

def build_diesel_momentum_factor(raw_df: pd.DataFrame, window: int = 5) -> pd.Series:
    """
    构建柴油价格动量因子

    参数：
    ----------
    raw_df : pd.DataFrame
        原始柴油价格数据，必须包含 'Date' 和 'Price' 列
    window : int
        动量窗口天数，默认 5

    返回：
    ----------
    pd.Series
        日期为索引，值为动量因子，Series 名称自动带上窗口长度
    """
    df = raw_df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df.set_index('Date', inplace=True)

    # 计算动量
    factor = (df['Price'] - df['Price'].shift(window)) / df['Price'].shift(window)
    factor.name = f'diesel_momentum_factor_{window}d'

    return factor


if __name__ == "__main__":
    # ---------- 用户可修改 ----------
    excel_path = "USA Daily Diesel Spot Price.xlsx"  # Excel 文件路径
    output_dir = "."  # 输出文件夹
    window = 10       # 动量窗口天数，可自定义
    # -------------------------------

    # 读取数据
    raw_df = pd.read_excel(excel_path)

    # 构建因子
    momentum_factor = build_diesel_momentum_factor(raw_df, window=window)

    # 输出 CSV
    output_csv = os.path.join(output_dir, f"{momentum_factor.name}.csv")
    momentum_factor.reset_index().to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("=== Diesel Momentum Factor 构建完成 ===")
    print(f"窗口长度: {window} 天")
    print(f"CSV 文件保存到: {output_csv}")
    print("\n预览：")
    print(momentum_factor.head(10))
