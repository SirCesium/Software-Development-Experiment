"""SCS-CN 模型边界条件与物理约束测试。"""

from __future__ import annotations

import unittest

import numpy as np

from scscn_runoff import calculate_retention, calculate_runoff


class TestSCSCNRunoff(unittest.TestCase):
    def test_zero_rainfall_returns_zero(self) -> None:
        self.assertEqual(calculate_runoff(0, 80), 0.0)

    def test_p_less_than_initial_abstraction_returns_zero(self) -> None:
        cn = 80
        s = calculate_retention(cn)
        ia = 0.2 * s
        self.assertEqual(calculate_runoff(ia - 0.1, cn), 0.0)

    def test_p_equal_initial_abstraction_returns_zero(self) -> None:
        cn = 80
        s = calculate_retention(cn)
        ia = 0.2 * s
        self.assertEqual(calculate_runoff(ia, cn), 0.0)

    def test_known_normal_case(self) -> None:
        runoff = calculate_runoff(50, 80)
        self.assertAlmostEqual(runoff, 13.8, places=1)

    def test_maximum_cn_returns_rainfall(self) -> None:
        self.assertEqual(calculate_runoff(50, 100), 50.0)

    def test_zero_cn_returns_zero(self) -> None:
        self.assertEqual(calculate_runoff(50, 0), 0.0)

    def test_runoff_never_exceeds_rainfall(self) -> None:
        rainfall_values = np.linspace(0, 200, 41)
        cn_values = np.array([0, 30, 60, 70, 80, 90, 95, 100])
        for cn in cn_values:
            runoff = calculate_runoff(rainfall_values, cn)
            self.assertTrue(np.all(runoff <= rainfall_values + 1e-9))
            self.assertTrue(np.all(runoff >= 0))

    def test_higher_cn_produces_more_runoff(self) -> None:
        rainfall = 50
        cn_values = np.array([60, 70, 80, 90, 95, 100])
        runoff = calculate_runoff(rainfall, cn_values)
        self.assertTrue(np.all(np.diff(runoff) >= 0))

    def test_vectorized_inputs(self) -> None:
        rainfall = np.array([0, 25, 50])
        cn = np.array([80, 80, 80])
        runoff = calculate_runoff(rainfall, cn)
        self.assertEqual(runoff.shape, rainfall.shape)
        self.assertAlmostEqual(runoff[-1], 13.8, places=1)

    def test_invalid_inputs_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            calculate_runoff(-1, 80)
        with self.assertRaises(ValueError):
            calculate_runoff(50, -1)
        with self.assertRaises(ValueError):
            calculate_runoff(50, 101)


if __name__ == "__main__":
    unittest.main(verbosity=2)
