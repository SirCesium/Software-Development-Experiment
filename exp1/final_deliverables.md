# 实验 1 最终交付清单

## 必交文件

| 文件 | 状态 | 说明 |
| --- | --- | --- |
| `weather_monitor.py` | 已完成 | 主程序，包含 API 获取、阈值告警、日志记录和 Streamlit 仪表盘 |
| `alert_log.txt` | 已完成 | 红色告警日志，已用 `21.0 mm/h` 示例数据测试写入 |
| `prompt_log.md` | 已完成 | 中文记录 AI 交互、人工修正和真实 API 验证过程 |
| `dashboard_screenshot.png` | 已完成 | 仪表盘效果截图 |

## 补充文件

| 文件 | 说明 |
| --- | --- |
| `testing_validation.md` | Part 4 测试与物理合理性验证记录 |
| `manual_records.md` | 需要你手动截图和记录的内容 |
| `requirements.txt` | Python 依赖 |
| `rainfall_history.csv` | 当前真实 API 历史观测数据 |
| `.streamlit/secrets.toml` | 本地 API Key 配置文件，不建议公开提交 |
| `.gitignore` | 防止密钥、日志和缓存误提交 |

## 运行方式

在 `exp1` 目录下运行：

```powershell
python -m streamlit run weather_monitor.py
```

浏览器打开后：

1. 城市名称保持 `Beijing` 或输入其他城市。
2. 关闭“使用示例数据”以读取真实 API。
3. 若要测试红色告警，打开“使用示例数据”，把示例降雨强度调到 `21.0 mm/h`。

## 实验要求对应关系

| 文档任务 | 完成位置 |
| --- | --- |
| Part 1 API Integration | `fetch_weather()`、`extract_rainfall_mm_h()` |
| Part 2 Alert Logic | `check_alert()`、`log_alert()` |
| Part 3 Dashboard Creation | `render_dashboard()` |
| Part 4 Testing & Validation | `testing_validation.md` |
| Prompt Log | `prompt_log.md` |
| Dashboard Screenshot | `dashboard_screenshot.png`，建议另存一张实时 API 截图 |

## 最终结论

系统已成功接入 OpenWeatherMap 实时接口。当前北京降雨强度为 `0.0 mm/h`，未达到黄色或红色阈值，因此绿色状态合理。通过示例数据 `21.0 mm/h` 已验证红色告警和日志写入功能正常。
