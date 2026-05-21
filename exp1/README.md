# Experiment 1: Short-term Rainfall Forecasting & Alert System

本项目对应实验文档 **Experiment1_Rainfall_Alert.docx**，目标是构建一个基于 OpenWeatherMap API 的短时降雨监测与告警系统。系统可以读取实时天气数据，提取小时降雨强度，根据阈值判断告警等级，并通过 Streamlit 仪表盘展示结果。

## 1. 项目运行方式

先安装依赖：

```powershell
pip install -r requirements.txt
```

然后在 `exp1` 目录下运行：

```powershell
python -m streamlit run weather_monitor.py
```

浏览器打开后：

- 在左侧输入城市名称，例如 `Beijing`、`Xian`、`Xiamen`。
- 关闭“使用示例数据”可以读取 OpenWeatherMap 实时接口。
- 打开“使用示例数据”可以手动测试黄色或红色告警阈值。

> 注意：真实 API Key 保存在本地 `.streamlit/secrets.toml` 中。该文件包含个人api key。

## 2. 实验文档任务完成位置

| 实验任务 | 要求内容 | 完成位置 |
| --- | --- | --- |
| Part 1: API Integration | 调用 OpenWeatherMap API，提取降雨强度，处理接口错误 | `weather_monitor.py` 中的 `fetch_weather()` 和 `extract_rainfall_mm_h()` |
| Part 2: Alert Logic Implementation | 实现绿色、黄色、红色阈值判断；红色告警写入日志 | `weather_monitor.py` 中的 `check_alert()` 和 `log_alert()` |
| Part 3: Dashboard Creation | 使用 Streamlit 展示标题、当前降雨、告警状态、历史曲线、自动刷新 | `weather_monitor.py` 中的 `render_dashboard()` |
| Part 4: Testing & Validation | 测试不同城市、验证阈值、检查日志、说明物理合理性 | `testing_validation.md` |
| Prompt Log | 记录 AI 交互、修正过程和真实 API 验证 | `prompt_log.md` |

## 3. 关键内容

实验文档要求的四个关键交付物如下：

| Deliverable | 文件位置 | 说明 |
| --- | --- | --- |
| `weather_monitor.py` | `weather_monitor.py` | 主应用代码。包含 API 调用、降雨强度提取、阈值告警、日志写入、Streamlit 仪表盘。 |
| `alert_log.txt` | `alert_log.txt` | 红色告警日志。使用示例数据 `21.0 mm/h` 触发红色告警后，系统会写入时间戳、城市、降雨强度、告警等级和数据来源。 |
| `prompt_log.md` | `prompt_log.md` | AI 交互记录。记录了从读取实验要求、生成 API 代码、实现告警逻辑、构建仪表盘，到配置真实 API 和完成测试验证的全过程。 |
| Screenshot of working dashboard | `Screenshot/` 文件夹 | 工作仪表盘截图。当前包含 `Beijing.png`、`Xian.png`、`Xiamen.png`，可用于证明系统已成功运行。 |

## 4. 文件结构说明

```text
exp1/
├── weather_monitor.py          # 主应用代码
├── alert_log.txt               # 红色告警日志
├── prompt_log.md               # AI Prompt Log
├── testing_validation.md       # Part 4 测试与验证记录
├── manual_records.md           # 需要手动记录或截图的说明
├── final_deliverables.md       # 最终交付清单
├── requirements.txt            # Python 依赖
├── rainfall_history.csv        # 本地历史降雨记录
├── find_rainy_cities.py        # 辅助脚本：查询当前有降雨的城市
├── Screenshot/                 # 仪表盘截图文件夹
│   ├── Beijing.png
│   ├── Xian.png
│   └── Xiamen.png
└── .streamlit/
    └── secrets.toml            # 本地 API Key 配置，不建议上传 GitHub
```

## 5. 告警阈值说明

系统按照实验文档要求使用以下阈值：

| 降雨强度 | 告警等级 | 系统行为 |
| ---: | --- | --- |
| `< 10 mm/h` | 绿色 | 正常状态，不写入红色告警日志 |
| `10 <= rainfall < 20 mm/h` | 黄色 | 中等降雨，提示持续关注 |
| `>= 20 mm/h` | 红色 | 强降雨告警，写入 `alert_log.txt` |

## 6. 测试与验证摘要

已完成以下验证：

- 北京实时接口可用，当前返回 `0.0 mm/h`，告警等级为绿色。
- 厦门实时接口返回小雨，约 `0.2 mm/h`，告警等级为绿色。
- 使用示例数据 `21.0 mm/h` 成功触发红色告警，并写入 `alert_log.txt`。
- 阈值边界 `0.0`、`9.9`、`10.0`、`19.9`、`20.0` 已测试通过。
- 详细记录见 `testing_validation.md`。

需要自行配置 OpenWeatherMap API Key 到 `.streamlit/secrets.toml` 或环境变量 `OPENWEATHER_API_KEY`。
