# -*- coding: utf-8 -*-
"""
环境检查：运行本脚本可检测 Python 版本与依赖是否齐全。
在「相关性分析和去重」目录下运行：python check_env.py
"""
import sys

def main():
    print("=" * 50)
    print("环境检查")
    print("=" * 50)
    print("Python 版本:", sys.version)
    if sys.version_info < (3, 7):
        print("[警告] 建议使用 Python 3.7 或更高版本")
    print()

    required = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("sklearn", "scikit-learn"),
    ]
    missing = []
    for mod, pip_name in required:
        try:
            __import__(mod)
            print("[OK]", mod)
        except ImportError:
            print("[缺失]", mod, " -> 请安装: pip install", pip_name)
            missing.append(pip_name)

    if missing:
        print()
        print("请在本目录或任意终端执行以下命令安装缺失依赖：")
        print("  pip install " + " ".join(missing))
        print()
        print("或安装全部推荐依赖：")
        print("  pip install -r requirements.txt")
        return 1
    print()
    print("依赖齐全，可以运行：python run_pipeline.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
