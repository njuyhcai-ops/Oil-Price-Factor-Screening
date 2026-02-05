from pathlib import Path
import pandas as pd

def calc_momentum_factor(file_path, window=1, output_file="oil_consumption_momentum_factor.csv"):
    df = pd.read_excel(file_path)
    yearly_consumption = df.groupby('Year')['Value'].sum().reset_index()
    yearly_consumption['Momentum'] = yearly_consumption['Value'].pct_change(periods=window)

    factor_df = yearly_consumption[['Year', 'Momentum']]
    factor_df.columns = ['Date', 'Oil Consumption Momentum Factor']
    factor_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    return factor_df


if __name__ == "__main__":
    # 获取当前脚本所在文件夹
    current_dir = Path(__file__).parent

    # Excel 与脚本同一目录
    file_path = current_dir / "Oil Consumption in Barrels.xlsx"

    momentum_df = calc_momentum_factor(file_path, window=1)
    print(momentum_df.head())
