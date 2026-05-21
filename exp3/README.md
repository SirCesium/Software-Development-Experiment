# Experiment 3: Reservoir Dispatch Optimization

本目录对应实验文档 **Experiment3_Reservoir_Optimization.docx**，主题是 7 天干旱期水库调度优化。目标是在满足库容、水量平衡和生态流量约束的前提下，尽量提高水电收益，并分析收益与生态目标之间的权衡关系。

## 1. 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

运行水库优化并生成最优调度表：

```powershell
python reservoir_optimize.py
```

生成收益-生态权衡图：

```powershell
python tradeoff_analysis.py
```

生成约束验证报告：

```powershell
python validate_solution.py
```

## 2. 实验任务完成位置

| 实验任务 | 要求内容 | 完成位置 |
| --- | --- | --- |
| Part 1: Problem Formulation | 定义 7 个决策变量、目标函数和约束 | `reservoir_optimize.py`、本文档第 5 节 |
| Part 2: Implementation | 使用 `scipy.optimize` 求解最优出库 | `reservoir_optimize.py` |
| Part 3: Trade-off Analysis | 不同生态权重下分析收益-生态权衡并绘制 Pareto 图 | `tradeoff_analysis.py`、`tradeoff_analysis.png` |
| Part 4: Validation | 验证库容、出库、生态流量、水量平衡和收益计算 | `validate_solution.py`、`validation_report.txt` |
| Prompt Log | 记录 AI 交互和人工修正 | `prompt_log.md` |

## 3. 关键内容

| 内容 | 文件位置 | 说明 |
| --- | --- | --- |
| 优化主程序 | `reservoir_optimize.py` | 实现水库调度优化，包含目标函数、约束、求解和调度表生成。 |
| 最优调度表 | `optimal_schedule.csv` | 7 天最优放水调度表，对应任务文档 Deliverables 中的 optimal schedule。 |
| 权衡分析图 | `tradeoff_analysis.png` | 收益-生态缺口 Pareto frontier 图，对应任务文档 Deliverables 中的 tradeoff plot。 |
| AI 交互记录 | `prompt_log.md` | AI 交互、建模过程和人工修正记录。 |
| 约束验证报告 | `validation_report.txt` | 库容、出库、生态流量、水量平衡和收益计算验证结果。 |

## 4. 文件结构

```text
exp3/
├── reservoir_optimize.py
├── optimal_schedule.csv
├── tradeoff_analysis.py
├── tradeoff_analysis.png
├── tradeoff_results.csv
├── validate_solution.py
├── validation_report.txt
├── prompt_log.md
├── requirements.txt
└── README.md
```

## 5. 优化问题 Formulation

决策变量：

```text
Q = [Q1, Q2, Q3, Q4, Q5, Q6, Q7]
```

其中 `Qt` 为第 `t` 天平均出库流量，单位为 `m3/s`。

目标函数：

```text
maximize total hydropower revenue
```

程序中使用 `scipy.optimize`，因此实际求解时转化为最小化负收益：

```text
minimize -total_revenue
```

水量平衡：

```text
V(t+1) = V(t) + (Inflow(t) - Release(t)) * 86400
```

约束：

```text
100,000 <= V(t) <= 1,000,000
10 <= Q(t) <= 100
```

权衡分析中，为展示生态缺口代价，另设软生态约束情景，允许 `Q(t) < 10`，并用缺口惩罚系数分析收益与生态之间的 trade-off。最终提交的最优调度仍采用严格生态约束。

## 6. 结果摘要

最终严格生态约束方案满足：

- 所有出库 `Q_release >= 10 m3/s`
- 所有出库 `Q_release <= 100 m3/s`
- 所有库容位于 `100,000` 到 `1,000,000 m3`
- 逐日水量平衡误差接近 0
- 生态缺口为 0

详细结果见：

- `optimal_schedule.csv`
- `validation_report.txt`
- `tradeoff_results.csv`
