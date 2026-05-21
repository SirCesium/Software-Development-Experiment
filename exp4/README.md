# Experiment 4: Flood Inundation Analysis (DEM-based)

本目录对应实验文档 **Experiment4_Flood_Inundation.docx**，主题是基于 DEM 的洪水淹没分析。项目使用合成 DEM 数据，通过空间比较算法判断不同水位下的淹没范围，计算淹没面积比例，并生成洪水范围图和水位-淹没比例曲线。

## 1. 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

运行完整分析：

```powershell
python flood_inundation.py
```

运行后会生成：

- `dem_data.npy`
- `flood_extent_40m.png`
- `flood_extent_50m.png`
- `flood_curve.png`
- `validation_report.txt`

## 2. 实验任务完成位置

| 实验任务 | 要求内容 | 完成位置 |
| --- | --- | --- |
| Part 1: DEM Data Preparation | 生成或读取 100×100 DEM 数据 | `load_dem()`、`generate_synthetic_dem()`、`dem_data.npy` |
| Part 2: Flood Simulation | 计算淹没掩膜、水深和淹没面积比例 | `calculate_flood()` |
| Part 3: Visualization | 生成 DEM、淹没范围叠加、水深热力图 | `visualize_flood()`、`flood_extent_40m.png`、`flood_extent_50m.png` |
| Part 4: Dynamic Simulation | 模拟 40-50 m 水位上升并绘制曲线 | `simulate_rising_water()`、`plot_flood_curve()`、`flood_curve.png` |
| Part 5: Validation | 验证单调性、最大水深和边界情况 | `validate_physical_correctness()`、`validation_report.txt` |
| Prompt Log | 记录 AI 交互和人工修正 | `prompt_log.md` |

## 3. 关键内容

| 内容 | 文件位置 | 说明 |
| --- | --- | --- |
| 主实现代码 | `flood_inundation.py` | 包含 DEM 生成、洪水计算、可视化、动态模拟和验证逻辑。 |
| DEM 数据 | `dem_data.npy` | 100×100 合成 DEM，海拔范围约 30-80 m。 |
| 40 m 水位淹没图 | `flood_extent_40m.png` | 展示 40 m 水位下的 DEM、淹没范围和水深。 |
| 50 m 水位淹没图 | `flood_extent_50m.png` | 展示 50 m 水位下的 DEM、淹没范围和水深。 |
| 水位-淹没比例曲线 | `flood_curve.png` | 展示 40-50 m 水位下淹没面积比例变化。 |
| AI 交互记录 | `prompt_log.md` | 记录 AI 辅助生成代码、修正和验证过程。 |
| 验证报告 | `validation_report.txt` | 记录物理正确性检查结果。 |

## 4. 任务文档对应关系

| 文档要求 | 本项目文件 |
| --- | --- |
| `flood_inundation.py - Main implementation` | `flood_inundation.py` |
| `dem_data.npy - DEM data file` | `dem_data.npy` |
| `flood_extent_40m.png - Visualization at 40m water level` | `flood_extent_40m.png` |
| `flood_extent_50m.png - Visualization at 50m water level` | `flood_extent_50m.png` |
| `flood_curve.png - Water level vs. flooded percentage plot` | `flood_curve.png` |
| `prompt_log.md - Documentation of AI interactions` | `prompt_log.md` |

## 5. 文件结构

```text
exp4/
├── flood_inundation.py
├── dem_data.npy
├── flood_extent_40m.png
├── flood_extent_50m.png
├── flood_curve.png
├── validation_report.txt
├── prompt_log.md
├── requirements.txt
└── README.md
```

## 6. 方法说明

淹没判断：

```text
Flooded if elevation < water_level
```

水深计算：

```text
Depth = water_level - elevation, if flooded
Depth = 0, otherwise
```

淹没面积百分比：

```text
Flooded percentage = flooded cells / total cells * 100
```

## 7. 验证摘要

程序验证以下物理条件：

- 水位升高时，淹没面积比例单调不减。
- 最大水深等于 `water_level - min_elevation`。
- 淹没比例始终在 `0-100%` 之间。
- 水位低于 DEM 最低高程时，淹没比例为 `0%`。
- 水位高于 DEM 最高高程时，淹没比例为 `100%`。

详细结果见 `validation_report.txt`。
