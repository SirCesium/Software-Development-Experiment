# Experiment 2: Hydrological Modeling - SCS-CN Runoff Calculation

本目录对应实验文档 **Experiment2_SCSCN_Runoff.docx**，主题是使用 SCS-CN 方法计算降雨直接径流，并完成边界测试、敏感性分析和物理合理性验证。

## 1. 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

运行样例计算：

```powershell
python scscn_runoff.py
```

运行测试：

```powershell
python -m unittest test_scscn.py
```

生成敏感性分析图：

```powershell
python sensitivity_analysis.py
```

## 2. 实验任务完成位置

| 实验任务 | 要求内容 | 完成位置 |
| --- | --- | --- |
| Part 1: Formula Implementation | 实现 SCS-CN 公式，处理边界条件 | `scscn_runoff.py` |
| Part 2: Boundary Condition Testing | 编写边界测试，验证 `P=0`、`P<Ia`、`P=Ia`、`CN=100` 等情况 | `test_scscn.py` |
| Part 3: Sensitivity Analysis | 固定 `P=50mm`，分析不同 CN 的径流变化并绘图 | `sensitivity_analysis.py`、`runoff_comparison.png` |
| Part 4: Validation & Documentation | 验证物理正确性，说明 AI 错误与修正 | `validation_report.md`、`prompt_log.md` |

## 3. 关键内容

| Deliverable | 文件位置 | 说明 |
| --- | --- | --- |
| `scscn_runoff.py` | `scscn_runoff.py` | 主实现文件，包含 `calculate_runoff()` 函数。 |
| `test_scscn.py` | `test_scscn.py` | 综合测试文件，覆盖实验文档要求的边界条件。 |
| `sensitivity_analysis.py` | `sensitivity_analysis.py` | 敏感性分析与可视化脚本。 |
| `runoff_comparison.png` | `runoff_comparison.png` | 生成图像，包含 CN vs Q 和不同 CN 的 Rainfall vs Runoff 对比。 |
| `prompt_log.md` | `prompt_log.md` | AI 交互记录与人工修正说明。 |

## 4. 文件结构

```text
exp2/
├── scscn_runoff.py
├── test_scscn.py
├── sensitivity_analysis.py
├── runoff_comparison.png
├── sensitivity_results.csv
├── validation_report.md
├── prompt_log.md
├── requirements.txt
└── README.md
```

## 5. 公式与阈值

SCS-CN 公式：

```text
S = (25400 / CN) - 254
Ia = 0.2 * S
Q = (P - Ia)^2 / (P - Ia + S), 当 P > Ia
Q = 0, 当 P <= Ia
```

物理边界：

- `CN = 0`：全部入渗，`Q = 0`
- `CN = 100`：不透水地表，`Q = P`
- 所有情况下 `0 <= Q <= P`

## 6. 结果摘要

对于文档样例 `P = 50 mm, CN = 80`：

```text
S = 63.5 mm
Ia = 12.7 mm
Q = 13.8 mm
```

固定 `P = 50 mm` 时，CN 越大，径流越大，符合水文学物理规律。
