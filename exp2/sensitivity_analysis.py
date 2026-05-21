"""SCS-CN 敏感性分析与可视化。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scscn_runoff import calculate_runoff


OUTPUT_PLOT = Path("runoff_comparison.png")
OUTPUT_TABLE = Path("sensitivity_results.csv")


def build_sensitivity_table(fixed_rainfall: float = 50.0) -> pd.DataFrame:
    """计算固定降雨量下不同 CN 的径流深。"""
    cn_values = np.array([60, 70, 80, 90, 95, 100], dtype=float)
    runoff_values = calculate_runoff(fixed_rainfall, cn_values)
    return pd.DataFrame(
        {
            "CN": cn_values.astype(int),
            "Rainfall_mm": fixed_rainfall,
            "Runoff_mm": np.round(runoff_values, 2),
            "Runoff_ratio": np.round(runoff_values / fixed_rainfall, 3),
        }
    )


def create_plots() -> pd.DataFrame:
    """生成 CN 敏感性图和降雨-径流对比图。"""
    fixed_rainfall = 50.0
    cn_values = np.array([60, 70, 80, 90, 95, 100], dtype=float)
    rainfall_range = np.linspace(0, 100, 101)
    sensitivity = build_sensitivity_table(fixed_rainfall)

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    axes[0].plot(sensitivity["CN"], sensitivity["Runoff_mm"], marker="o", linewidth=2)
    axes[0].set_title("固定降雨 P = 50 mm 时 CN 对径流的影响")
    axes[0].set_xlabel("Curve Number (CN)")
    axes[0].set_ylabel("Runoff Q (mm)")
    axes[0].grid(True, alpha=0.3)
    for _, row in sensitivity.iterrows():
        axes[0].annotate(
            f"{row['Runoff_mm']:.1f}",
            (row["CN"], row["Runoff_mm"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
        )

    for cn in cn_values:
        runoff_curve = calculate_runoff(rainfall_range, cn)
        axes[1].plot(rainfall_range, runoff_curve, linewidth=2, label=f"CN={int(cn)}")
    axes[1].plot(rainfall_range, rainfall_range, linestyle="--", color="black", alpha=0.5, label="Q = P 上限")
    axes[1].set_title("不同 CN 条件下的降雨-径流关系")
    axes[1].set_xlabel("Rainfall P (mm)")
    axes[1].set_ylabel("Runoff Q (mm)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.suptitle("SCS-CN Runoff Sensitivity Analysis", fontsize=16, fontweight="bold")
    fig.savefig(OUTPUT_PLOT, dpi=200)
    plt.close(fig)

    sensitivity.to_csv(OUTPUT_TABLE, index=False, encoding="utf-8")
    return sensitivity


if __name__ == "__main__":
    table = create_plots()
    print(table.to_string(index=False))
    print(f"\n图像已保存到：{OUTPUT_PLOT}")
    print(f"结果表已保存到：{OUTPUT_TABLE}")
