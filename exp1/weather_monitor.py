"""
短时降雨监测与告警系统

运行方式：
    streamlit run weather_monitor.py

说明：
    1. 如果提供 OpenWeatherMap API Key，系统会读取真实天气数据。
    2. 如果没有 API Key，系统会自动使用中文示例数据，便于课堂演示和阈值测试。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import altair as alt

try:
    import requests
except ImportError:  # pragma: no cover - 用于给缺少依赖的环境提供清晰提示
    requests = None

try:
    import streamlit as st
except ImportError:  # pragma: no cover - 阈值逻辑测试不依赖 Streamlit
    st = None


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_CITY = "Beijing"
ALERT_THRESHOLD = 20.0
LOG_FILE = Path(__file__).with_name("alert_log.txt")
HISTORY_FILE = Path(__file__).with_name("rainfall_history.csv")


@dataclass(frozen=True)
class WeatherRecord:
    city: str
    rainfall_mm_h: float
    description: str
    source: str
    observed_at: datetime


@dataclass(frozen=True)
class AlertStatus:
    level: str
    label: str
    color: str
    message: str
    should_log: bool


class WeatherAPIError(RuntimeError):
    """天气接口调用失败时抛出的异常。"""


def get_api_key() -> str:
    """优先从 Streamlit secrets 读取 API Key，其次读取环境变量。"""
    if st is not None:
        try:
            return str(st.secrets.get("OPENWEATHER_API_KEY", "")).strip()
        except Exception:
            pass
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def extract_rainfall_mm_h(payload: dict[str, Any]) -> float:
    """
    从 OpenWeatherMap 响应中提取小时降雨强度。

    OpenWeatherMap 的 rain 字段可能包含 1h 或 3h。若只有 3h 数据，
    这里除以 3 得到近似的每小时降雨强度。
    """
    rain = payload.get("rain") or {}
    if "1h" in rain:
        return float(rain["1h"])
    if "3h" in rain:
        return float(rain["3h"]) / 3.0
    return 0.0


def fetch_weather(city: str, api_key: str | None = None) -> WeatherRecord:
    """调用 OpenWeatherMap 当前天气接口，返回标准化后的降雨记录。"""
    if requests is None:
        raise WeatherAPIError("缺少 requests 依赖，请先安装 requirements.txt 中的依赖。")

    key = (api_key or get_api_key()).strip()
    if not key:
        raise WeatherAPIError("未配置 OpenWeatherMap API Key。")

    params = {
        "q": city,
        "appid": key,
        "units": "metric",
        "lang": "zh_cn",
    }

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherAPIError(f"天气接口请求失败：{exc}") from exc

    payload = response.json()
    description = "无天气描述"
    weather_items = payload.get("weather") or []
    if weather_items:
        description = weather_items[0].get("description", description)

    return WeatherRecord(
        city=payload.get("name") or city,
        rainfall_mm_h=extract_rainfall_mm_h(payload),
        description=description,
        source="OpenWeatherMap 实时接口",
        observed_at=datetime.now(),
    )


def get_sample_weather(city: str, rainfall_mm_h: float) -> WeatherRecord:
    """生成示例数据，用于没有 API Key 或课堂测试阈值时演示。"""
    if rainfall_mm_h >= 20:
        description = "强降雨示例"
    elif rainfall_mm_h >= 10:
        description = "中等降雨示例"
    elif rainfall_mm_h > 0:
        description = "小雨示例"
    else:
        description = "无降雨示例"

    return WeatherRecord(
        city=city,
        rainfall_mm_h=float(rainfall_mm_h),
        description=description,
        source="本地示例数据",
        observed_at=datetime.now(),
    )


def check_alert(rainfall_mm_h: float) -> AlertStatus:
    """根据实验要求判断绿色、黄色、红色告警等级。"""
    if rainfall_mm_h < 10:
        return AlertStatus(
            level="green",
            label="绿色",
            color="#238636",
            message="正常：当前降雨小于 10 mm/h。",
            should_log=False,
        )
    if rainfall_mm_h < ALERT_THRESHOLD:
        return AlertStatus(
            level="yellow",
            label="黄色",
            color="#f2cc0c",
            message="中等：当前降雨达到 10 mm/h，请持续关注。",
            should_log=False,
        )
    return AlertStatus(
        level="red",
        label="红色",
        color="#d1242f",
        message="强降雨告警：当前降雨达到或超过 20 mm/h，请启动排水与巡查预案。",
        should_log=True,
    )


def log_alert(record: WeatherRecord, status: AlertStatus) -> None:
    """当红色告警触发时，将事件写入日志文件。"""
    if not status.should_log:
        return

    line = (
        f"{record.observed_at:%Y-%m-%d %H:%M:%S} | "
        f"城市={record.city} | "
        f"降雨强度={record.rainfall_mm_h:.1f} mm/h | "
        f"等级={status.label} | "
        f"来源={record.source}\n"
    )
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line)


def append_history(record: WeatherRecord, status: AlertStatus) -> None:
    """保存历史降雨记录，供仪表盘绘制折线图。"""
    if HISTORY_FILE.exists():
        try:
            history = pd.read_csv(HISTORY_FILE)
            city_history = history[history["city"] == record.city]
            if not city_history.empty:
                last = city_history.iloc[-1]
                last_time = pd.to_datetime(last["time"]).to_pydatetime()
                same_value = abs(float(last["rainfall_mm_h"]) - record.rainfall_mm_h) < 0.05
                same_source = str(last["source"]) == record.source
                recent = record.observed_at - last_time < timedelta(minutes=4)
                if same_value and same_source and recent:
                    return
        except Exception:
            pass

    row = pd.DataFrame(
        [
            {
                "time": record.observed_at.strftime("%Y-%m-%d %H:%M:%S"),
                "city": record.city,
                "rainfall_mm_h": record.rainfall_mm_h,
                "alert": status.label,
                "source": record.source,
            }
        ]
    )
    header = not HISTORY_FILE.exists()
    row.to_csv(HISTORY_FILE, mode="a", index=False, header=header, encoding="utf-8")


def load_recent_history(city: str, limit: int = 12) -> pd.DataFrame:
    """读取最近的历史记录。"""
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=["time", "time_label", "rainfall_mm_h"])

    history = pd.read_csv(HISTORY_FILE)
    history = history[history["city"] == city].tail(limit)
    if history.empty:
        return pd.DataFrame(columns=["time", "time_label", "rainfall_mm_h"])

    history["time"] = pd.to_datetime(history["time"])
    history["time_label"] = history["time"].dt.strftime("%m-%d %H:%M")
    return history[["time", "time_label", "rainfall_mm_h"]]


def render_dashboard() -> None:
    """渲染 Streamlit 仪表盘。"""
    if st is None:
        raise RuntimeError("缺少 streamlit 依赖，请先安装 requirements.txt 中的依赖。")

    st.set_page_config(page_title="降雨监测与告警", page_icon="🌧️", layout="wide")
    st.markdown("<meta http-equiv='refresh' content='300'>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("监测设置")
        city = st.text_input("城市名称", value=DEFAULT_CITY)
        use_sample = st.toggle("使用示例数据", value=not bool(get_api_key()))
        sample_rainfall = st.slider("示例降雨强度（mm/h）", 0.0, 60.0, 21.0, 0.5)
        st.caption("配置 OPENWEATHER_API_KEY 后可关闭示例数据，读取实时接口。")

    st.title(f"Rainfall Monitor - {city}")

    try:
        if use_sample:
            record = get_sample_weather(city, sample_rainfall)
        else:
            record = fetch_weather(city)
    except WeatherAPIError as exc:
        st.error(str(exc))
        st.info("已切换为示例数据，方便继续测试告警阈值。")
        record = get_sample_weather(city, sample_rainfall)

    status = check_alert(record.rainfall_mm_h)
    log_alert(record, status)
    append_history(record, status)

    metric_col, status_col, info_col = st.columns([1.1, 1, 1.2])
    with metric_col:
        st.metric("当前降雨强度", f"{record.rainfall_mm_h:.1f} mm/h")
    with status_col:
        st.markdown(
            f"""
            <div style="border-left: 12px solid {status.color}; padding: 0.7rem 1rem;
                        background: rgba(127, 127, 127, 0.08); border-radius: 6px;">
                <div style="font-size: 0.9rem;">告警状态</div>
                <div style="font-size: 2rem; font-weight: 700; color: {status.color};">
                    {status.label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with info_col:
        st.write(f"天气描述：{record.description}")
        st.write(f"数据来源：{record.source}")
        st.write(f"更新时间：{record.observed_at:%Y-%m-%d %H:%M:%S}")

    if status.should_log:
        st.error(status.message)
    elif status.level == "yellow":
        st.warning(status.message)
    else:
        st.success(status.message)

    st.subheader("最近降雨历史")
    history = load_recent_history(record.city)
    if history.empty:
        st.info("暂无历史记录，刷新后将逐步生成曲线。")
    else:
        st.caption("仅显示最近 12 条记录；相同城市在 4 分钟内重复返回相同降雨值时不会重复写入。")
        chart = (
            alt.Chart(history)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "time_label:N",
                    title="观测时间",
                    axis=alt.Axis(labelAngle=0, labelOverlap=True, labelLimit=90),
                    sort=None,
                ),
                y=alt.Y("rainfall_mm_h:Q", title="降雨强度 (mm/h)"),
                tooltip=[
                    alt.Tooltip("time_label:N", title="时间"),
                    alt.Tooltip("rainfall_mm_h:Q", title="降雨强度", format=".1f"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(chart, use_container_width=True)

    with st.expander("阈值说明", expanded=True):
        st.write("绿色：降雨强度 < 10 mm/h，状态正常。")
        st.write("黄色：10 ≤ 降雨强度 < 20 mm/h，中等降雨，需要关注。")
        st.write("红色：降雨强度 ≥ 20 mm/h，强降雨告警，并写入 alert_log.txt。")
        st.write("页面每 5 分钟自动刷新一次。")


def _run_threshold_self_test() -> None:
    """命令行快速验证阈值逻辑。"""
    cases = [(0, "绿色"), (9.9, "绿色"), (10, "黄色"), (19.9, "黄色"), (20, "红色")]
    for rainfall, expected in cases:
        actual = check_alert(rainfall).label
        assert actual == expected, f"{rainfall} mm/h 应为 {expected}，实际为 {actual}"
    print("阈值逻辑自检通过。")


if __name__ == "__main__":
    if st is None:
        _run_threshold_self_test()
    else:
        render_dashboard()
