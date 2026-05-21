# Experiment 1: Short-term Rainfall Forecasting & Alert System

本目录对应实验文档 **Experiment1_Rainfall_Alert.docx**，主题是短时降雨监测与阈值告警系统。项目使用 OpenWeatherMap API 获取实时天气数据，提取小时降雨强度，并通过 Streamlit 仪表盘展示降雨状态、告警等级和历史记录。

## 1. 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

在 `exp1` 目录下运行：

```powershell
python -m streamlit run weather_monitor.py
```

运行后：

- 在左侧输入城市名称，例如 `Beijing`、`Xian`、`Xiamen`。
- 关闭“使用示例数据”可以读取 OpenWeatherMap 实时接口。
- 打开“使用示例数据”可以手动测试黄色或红色告警阈值。

> 注意：真实 API Key 保存在本地 `.streamlit/secrets.toml` 中。该文件包含个人密钥，已通过 `.gitignore` 排除，不应上传到 GitHub。

## 2. 实验任务完成位置

| 实验任务 | 要求内容 | 完成位置 |
| --- | --- | --- |
| Part 1: API Integration | 调用 OpenWeatherMap API，提取降雨强度，处理接口错误 | `weather_monitor.py` 中的 `fetch_weather()` 和 `extract_rainfall_mm_h()` |
| Part 2: Alert Logic Implementation | 实现绿色、黄色、红色阈值判断；红色告警写入日志 | `weather_monitor.py` 中的 `check_alert()` 和 `log_alert()` |
| Part 3: Dashboard Creation | 使用 Streamlit 展示标题、当前降雨、告警状态、历史曲线和自动刷新 | `weather_monitor.py` 中的 `render_dashboard()` |
| Part 4: Testing & Validation | 测试不同城市、验证阈值、检查日志、说明物理合理性 | `testing_validation.md` |
| Prompt Log | 记录 AI 交互、人工修正和真实 API 验证 | `prompt_log.md` |

## 3. 关键内容

| 内容 | 文件位置 | 说明 |
| --- | --- | --- |
| 主应用代码 | `weather_monitor.py` | 包含 API 调用、降雨强度提取、阈值告警、日志写入、历史曲线和 Streamlit 仪表盘。 |
| 告警日志 | `alert_log.txt` | 红色告警日志。使用示例数据 `21.0 mm/h` 触发红色告警后，系统会写入时间戳、城市、降雨强度、告警等级和数据来源。 |
| AI 交互记录 | `prompt_log.md` | 记录从读取实验要求、生成 API 代码、实现告警逻辑、构建仪表盘，到配置真实 API 和完成测试验证的全过程。 |
| 工作仪表盘截图 | `Screenshot/` | 正式截图文件夹，当前包含 `Beijing.png`、`Xian.png`、`Xiamen.png`，用于证明系统已成功运行。 |
| 备用效果截图 | `dashboard_screenshot.png` | 早期生成的仪表盘效果截图，作为备用展示文件；正式提交和 README 说明优先参考 `Screenshot/` 文件夹。 |
| 测试与验证记录 | `testing_validation.md` | 对应 Part 4，记录城市对比、阈值测试、红色告警日志检查和物理合理性分析。 |

## 4. 任务文档对应关系

| 文档 Deliverable | 本项目文件 |
| --- | --- |
| `weather_monitor.py - Main application code` | `weather_monitor.py` |
| `alert_log.txt - Log of all triggered alerts` | `alert_log.txt` |
| `prompt_log.md - Documentation of AI interactions` | `prompt_log.md` |
| `Screenshot of working dashboard` | `Screenshot/` 文件夹；`dashboard_screenshot.png` 为备用效果截图 |

## 5. 文件结构

```text
exp1/
├── weather_monitor.py
├── alert_log.txt
├── prompt_log.md
├── testing_validation.md
├── manual_records.md
├── final_deliverables.md
├── requirements.txt
├── rainfall_history.csv
├── find_rainy_cities.py
├── dashboard_screenshot.png
├── Screenshot/
│   ├── Beijing.png
│   ├── Xian.png
│   └── Xiamen.png
└── .streamlit/
    └── secrets.toml       # 本地 API Key 配置，不上传 GitHub
```

## 6. 告警阈值说明

系统按照实验文档要求使用以下阈值：

| 降雨强度 | 告警等级 | 系统行为 |
| ---: | --- | --- |
| `< 10 mm/h` | 绿色 | 正常状态，不写入红色告警日志 |
| `10 <= rainfall < 20 mm/h` | 黄色 | 中等降雨，提示持续关注 |
| `>= 20 mm/h` | 红色 | 强降雨告警，写入 `alert_log.txt` |

## 7. 测试与验证摘要

已完成以下验证：

- 北京实时接口可用，返回 `0.0 mm/h` 时告警等级为绿色。
- 厦门实时接口曾返回小雨，约 `0.2 mm/h`，告警等级为绿色。
- 使用示例数据 `21.0 mm/h` 成功触发红色告警，并写入 `alert_log.txt`。
- 阈值边界 `0.0`、`9.9`、`10.0`、`19.9`、`20.0` 已测试通过。
- 详细记录见 `testing_validation.md`。
