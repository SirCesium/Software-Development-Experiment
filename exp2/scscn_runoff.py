"""SCS-CN 降雨径流计算模型。

本模块实现实验 2 要求的 Soil Conservation Service Curve Number
(SCS-CN) 方法，用于根据降雨量 P 和曲线数 CN 估算直接径流深 Q。
"""

from __future__ import annotations

from typing import Union

import numpy as np


NumberOrArray = Union[float, int, np.ndarray]


def calculate_retention(cn: NumberOrArray) -> NumberOrArray:
    """计算潜在最大滞蓄量 S。

    参数:
        cn: Curve Number，范围为 0 到 100。

    返回:
        S = (25400 / CN) - 254，单位为 mm。

    说明:
        CN = 0 表示全部入渗，此时 S 在物理上可视为无穷大。
        为了避免除零错误，程序用 np.inf 表示。
    """
    cn_array = np.asarray(cn, dtype=float)
    if np.any((cn_array < 0) | (cn_array > 100)):
        raise ValueError("CN 必须位于 0 到 100 之间。")

    retention = np.where(cn_array == 0, np.inf, (25400.0 / cn_array) - 254.0)
    if np.isscalar(cn):
        return float(retention)
    return retention


def calculate_runoff(p: NumberOrArray, cn: NumberOrArray) -> NumberOrArray:
    """使用 SCS-CN 方法计算直接径流深 Q。

    参数:
        p: 降雨深 P，单位为 mm，必须大于或等于 0。
        cn: Curve Number，范围为 0 到 100。

    返回:
        直接径流深 Q，单位为 mm。返回值满足 0 <= Q <= P。

    公式:
        S = (25400 / CN) - 254
        Ia = 0.2 * S
        当 P <= Ia 时，Q = 0
        当 P > Ia 时，Q = (P - Ia)^2 / (P - Ia + S)

    边界条件:
        CN = 0 时，全部入渗，Q = 0。
        CN = 100 时，不透水地表，Q = P。
    """
    p_array = np.asarray(p, dtype=float)
    cn_array = np.asarray(cn, dtype=float)

    if np.any(p_array < 0):
        raise ValueError("降雨深 P 不能为负数。")
    if np.any((cn_array < 0) | (cn_array > 100)):
        raise ValueError("CN 必须位于 0 到 100 之间。")

    p_b, cn_b = np.broadcast_arrays(p_array, cn_array)
    runoff = np.zeros_like(p_b, dtype=float)

    impervious = cn_b == 100
    runoff = np.where(impervious, p_b, runoff)

    valid = (cn_b > 0) & (cn_b < 100)
    if np.any(valid):
        s = (25400.0 / cn_b[valid]) - 254.0
        ia = 0.2 * s
        effective_rainfall = p_b[valid] - ia
        valid_runoff = np.where(
            effective_rainfall > 0,
            (effective_rainfall**2) / (effective_rainfall + s),
            0.0,
        )
        runoff[valid] = valid_runoff

    runoff = np.clip(runoff, 0.0, p_b)

    if np.isscalar(p) and np.isscalar(cn):
        return float(runoff)
    return runoff


def classify_cn_land_use(cn: float) -> str:
    """根据 CN 值给出简要土地利用解释，便于结果说明。"""
    if cn < 0 or cn > 100:
        raise ValueError("CN 必须位于 0 到 100 之间。")
    if cn < 70:
        return "林地或良好植被覆盖，入渗能力较强"
    if cn < 85:
        return "草地、居住区或中等入渗条件"
    if cn < 95:
        return "耕地或城市化区域，径流响应较强"
    return "铺装或近不透水地表，径流响应很强"


if __name__ == "__main__":
    example_p = 50.0
    example_cn = 80.0
    example_q = calculate_runoff(example_p, example_cn)
    example_s = calculate_retention(example_cn)
    example_ia = 0.2 * example_s
    print(f"P = {example_p:.1f} mm, CN = {example_cn:.0f}")
    print(f"S = {example_s:.1f} mm, Ia = {example_ia:.1f} mm")
    print(f"Q = {example_q:.1f} mm")
