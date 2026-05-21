"""7 天水库调度优化模型。

实验目标：
在干旱期同时考虑水电收益和下游生态流量需求，使用 scipy.optimize
生成满足物理约束的 7 天最优出库过程。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.optimize import linprog


SECONDS_PER_DAY = 24 * 60 * 60
WATER_DENSITY = 1000.0
GRAVITY = 9.81


@dataclass(frozen=True)
class ReservoirParams:
    """水库调度参数。"""

    initial_storage: float = 500_000.0
    min_storage: float = 100_000.0
    max_storage: float = 1_000_000.0
    min_ecological_release: float = 10.0
    max_release: float = 100.0
    inflow: tuple[float, ...] = (15, 12, 10, 8, 12, 15, 18)
    price: tuple[float, ...] = (0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10)
    hydropower_head_m: float = 25.0
    turbine_efficiency: float = 0.85


@dataclass(frozen=True)
class OptimizationResult:
    releases: np.ndarray
    storage: np.ndarray
    revenue: float
    ecological_deficit: float
    success: bool
    message: str


def energy_kwh_from_release(release_cms: np.ndarray, params: ReservoirParams) -> np.ndarray:
    """根据日均出库流量估算每日水电发电量，单位为 kWh。"""
    volume = release_cms * SECONDS_PER_DAY
    joules = WATER_DENSITY * GRAVITY * params.hydropower_head_m * params.turbine_efficiency * volume
    return joules / 3_600_000.0


def calculate_revenue(releases: Iterable[float], params: ReservoirParams = ReservoirParams()) -> float:
    """计算 7 天总水电收益，单位为美元。"""
    release_array = np.asarray(releases, dtype=float)
    prices = np.asarray(params.price, dtype=float)
    return float(np.sum(energy_kwh_from_release(release_array, params) * prices))


def calculate_storage_trajectory(
    releases: Iterable[float], params: ReservoirParams = ReservoirParams()
) -> np.ndarray:
    """根据水量平衡计算从第 0 天到第 7 天的库容序列。"""
    release_array = np.asarray(releases, dtype=float)
    inflow_array = np.asarray(params.inflow, dtype=float)
    storage = [params.initial_storage]
    current_storage = params.initial_storage

    for inflow, release in zip(inflow_array, release_array):
        current_storage = current_storage + (inflow - release) * SECONDS_PER_DAY
        storage.append(current_storage)

    return np.asarray(storage, dtype=float)


def ecological_deficit(releases: Iterable[float], params: ReservoirParams = ReservoirParams()) -> float:
    """计算生态流量缺口，单位为 (m3/s)-day。"""
    release_array = np.asarray(releases, dtype=float)
    deficit = np.maximum(0.0, params.min_ecological_release - release_array)
    return float(np.sum(deficit))


def _storage_constraints(params: ReservoirParams) -> list[dict]:
    """构造 SLSQP 使用的库容上下限不等式约束。"""

    def above_min(releases: np.ndarray) -> np.ndarray:
        storage = calculate_storage_trajectory(releases, params)[1:]
        return storage - params.min_storage

    def below_max(releases: np.ndarray) -> np.ndarray:
        storage = calculate_storage_trajectory(releases, params)[1:]
        return params.max_storage - storage

    return [
        {"type": "ineq", "fun": above_min},
        {"type": "ineq", "fun": below_max},
    ]


def optimize_reservoir(
    params: ReservoirParams = ReservoirParams(),
    ecology_penalty: float = 0.0,
    enforce_ecology: bool = True,
) -> OptimizationResult:
    """求解水库 7 天最优调度。

    参数:
        params: 水库参数。
        ecology_penalty: 软生态约束情景下的缺口惩罚系数。
        enforce_ecology: 为 True 时强制 Q_release >= Q_eco；为 False 时允许
            出现生态缺口，并通过 ecology_penalty 分析收益-生态权衡。
    """
    days = len(params.inflow)
    inflow = np.asarray(params.inflow, dtype=float)
    price = np.asarray(params.price, dtype=float)
    revenue_per_cms = energy_kwh_from_release(np.ones(days), params) * price

    # 严格生态方案只需要 release 变量；软生态方案增加 deficit 变量。
    variable_count = days if enforce_ecology else days * 2
    objective = np.zeros(variable_count, dtype=float)
    objective[:days] = -revenue_per_cms
    if not enforce_ecology:
        objective[days:] = ecology_penalty

    release_lower = params.min_ecological_release if enforce_ecology else 0.0
    bounds = [(release_lower, params.max_release) for _ in range(days)]
    if not enforce_ecology:
        bounds.extend([(0.0, params.min_ecological_release) for _ in range(days)])

    a_ub = []
    b_ub = []
    cumulative_inflow_volume = 0.0
    for day in range(days):
        cumulative_inflow_volume += inflow[day] * SECONDS_PER_DAY

        # V_t >= V_min -> sum(Q_i * dt) <= V0 + sum(I_i * dt) - V_min
        row_upper_release = np.zeros(variable_count, dtype=float)
        row_upper_release[: day + 1] = SECONDS_PER_DAY
        a_ub.append(row_upper_release)
        b_ub.append(params.initial_storage + cumulative_inflow_volume - params.min_storage)

        # V_t <= V_max -> -sum(Q_i * dt) <= -(V0 + sum(I_i * dt) - V_max)
        row_lower_release = np.zeros(variable_count, dtype=float)
        row_lower_release[: day + 1] = -SECONDS_PER_DAY
        a_ub.append(row_lower_release)
        b_ub.append(-(params.initial_storage + cumulative_inflow_volume - params.max_storage))

    if not enforce_ecology:
        for day in range(days):
            # deficit_day >= Q_eco - release_day
            # release_day + deficit_day >= Q_eco
            # -release_day - deficit_day <= -Q_eco
            row = np.zeros(variable_count, dtype=float)
            row[day] = -1.0
            row[days + day] = -1.0
            a_ub.append(row)
            b_ub.append(-params.min_ecological_release)

    result = linprog(
        c=objective,
        A_ub=np.asarray(a_ub, dtype=float),
        b_ub=np.asarray(b_ub, dtype=float),
        bounds=bounds,
        method="highs",
    )

    if result.x is None:
        releases = np.full(days, np.nan)
    else:
        releases = np.asarray(result.x[:days], dtype=float)
    releases[np.abs(releases) < 1e-9] = 0.0
    storage = calculate_storage_trajectory(releases, params)

    return OptimizationResult(
        releases=releases,
        storage=storage,
        revenue=calculate_revenue(releases, params),
        ecological_deficit=ecological_deficit(releases, params),
        success=bool(result.success),
        message=str(result.message),
    )


def build_schedule_dataframe(result: OptimizationResult, params: ReservoirParams) -> pd.DataFrame:
    """把优化结果整理为 7 天调度表。"""
    inflow = np.asarray(params.inflow, dtype=float)
    price = np.asarray(params.price, dtype=float)
    releases = result.releases
    energy = energy_kwh_from_release(releases, params)
    daily_revenue = energy * price

    return pd.DataFrame(
        {
            "Day": np.arange(1, len(inflow) + 1),
            "Inflow_m3s": np.round(inflow, 2),
            "Release_m3s": np.round(releases, 2),
            "End_Storage_m3": np.round(result.storage[1:], 2),
            "Price_USD_per_kWh": price,
            "Energy_kWh": np.round(energy, 2),
            "Daily_Revenue_USD": np.round(daily_revenue, 2),
            "Ecological_Deficit_m3s": np.round(np.maximum(0.0, params.min_ecological_release - releases), 4),
        }
    )


def save_optimal_schedule(path: str | Path = "optimal_schedule.csv") -> OptimizationResult:
    """求解严格生态约束方案，并保存最优 7 天调度表。"""
    params = ReservoirParams()
    result = optimize_reservoir(params=params, enforce_ecology=True)
    schedule = build_schedule_dataframe(result, params)
    schedule.to_csv(path, index=False, encoding="utf-8")
    return result


if __name__ == "__main__":
    params = ReservoirParams()
    result = save_optimal_schedule()
    schedule = build_schedule_dataframe(result, params)
    print(schedule.to_string(index=False))
    print(f"\nOptimization success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Total revenue: ${result.revenue:,.2f}")
    print(f"Ecological deficit: {result.ecological_deficit:.2f} (m3/s)-day")
