"""水库调度收益-生态权衡分析与 Pareto 图生成。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reservoir_optimize import ReservoirParams, optimize_reservoir


OUTPUT_PLOT = Path("tradeoff_analysis.png")
OUTPUT_TABLE = Path("tradeoff_results.csv")


def run_tradeoff_analysis() -> pd.DataFrame:
    """运行不同生态惩罚权重下的调度优化。"""
    params = ReservoirParams()
    penalties = [0, 250, 500, 1000, 2000, 5000, 10_000, 25_000, 50_000]
    records = []

    for penalty in penalties:
        result = optimize_reservoir(params=params, ecology_penalty=penalty, enforce_ecology=False)
        records.append(
            {
                "Ecology_Penalty": penalty,
                "Revenue_USD": round(result.revenue, 2),
                "Ecological_Deficit_m3s_day": round(result.ecological_deficit, 4),
                "Success": result.success,
                "Min_Release_m3s": round(float(np.min(result.releases)), 2),
                "Max_Release_m3s": round(float(np.max(result.releases)), 2),
            }
        )

    strict_result = optimize_reservoir(params=params, enforce_ecology=True)
    records.append(
        {
            "Ecology_Penalty": "strict_Qeco",
            "Revenue_USD": round(strict_result.revenue, 2),
            "Ecological_Deficit_m3s_day": round(strict_result.ecological_deficit, 4),
            "Success": strict_result.success,
            "Min_Release_m3s": round(float(np.min(strict_result.releases)), 2),
            "Max_Release_m3s": round(float(np.max(strict_result.releases)), 2),
        }
    )

    table = pd.DataFrame(records)
    table.to_csv(OUTPUT_TABLE, index=False, encoding="utf-8")
    return table


def create_tradeoff_plot(table: pd.DataFrame) -> None:
    """根据权衡分析结果生成 Pareto frontier 图。"""
    numeric = table[table["Ecology_Penalty"] != "strict_Qeco"].copy()
    strict = table[table["Ecology_Penalty"] == "strict_Qeco"].copy()

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    ax.plot(
        numeric["Ecological_Deficit_m3s_day"],
        numeric["Revenue_USD"],
        marker="o",
        linewidth=2,
        label="软生态约束情景",
    )
    if not strict.empty:
        ax.scatter(
            strict["Ecological_Deficit_m3s_day"],
            strict["Revenue_USD"],
            color="red",
            s=90,
            label="严格满足生态流量",
            zorder=3,
        )

    if not numeric.empty:
        no_penalty = numeric.iloc[0]
        ax.annotate(
            "penalty=0\nhighest revenue",
            (no_penalty["Ecological_Deficit_m3s_day"], no_penalty["Revenue_USD"]),
            textcoords="offset points",
            xytext=(-70, 10),
            fontsize=9,
            arrowprops={"arrowstyle": "->", "lw": 1},
        )
    if not strict.empty:
        strict_row = strict.iloc[0]
        ax.annotate(
            "strict ecological flow\nzero deficit",
            (strict_row["Ecological_Deficit_m3s_day"], strict_row["Revenue_USD"]),
            textcoords="offset points",
            xytext=(20, -35),
            fontsize=9,
            arrowprops={"arrowstyle": "->", "lw": 1},
        )

    ax.set_title("Reservoir Dispatch Trade-off: Revenue vs Ecological Deficit")
    ax.set_xlabel("Ecological deficit ((m3/s)-day)")
    ax.set_ylabel("Hydropower revenue (USD)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(OUTPUT_PLOT, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    result_table = run_tradeoff_analysis()
    create_tradeoff_plot(result_table)
    print(result_table.to_string(index=False))
    print(f"\n图像已保存到：{OUTPUT_PLOT}")
