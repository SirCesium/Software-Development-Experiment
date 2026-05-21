"""查询当前有降雨的城市，供实验截图选择使用。"""

from __future__ import annotations

import re
import time
from pathlib import Path

import requests


def read_api_key() -> str:
    text = Path(".streamlit/secrets.toml").read_text(encoding="utf-8")
    match = re.search(r'OPENWEATHER_API_KEY\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("未找到 OPENWEATHER_API_KEY。")
    return match.group(1)


def rainfall_from_payload(payload: dict) -> float:
    rain = payload.get("rain") or {}
    if "1h" in rain:
        return float(rain["1h"])
    if "3h" in rain:
        return float(rain["3h"]) / 3.0
    return 0.0


def main() -> None:
    api_key = read_api_key()
    cities = [
        "Guangzhou",
        "Shenzhen",
        "Haikou",
        "Sanya",
        "Nanning",
        "Guilin",
        "Kunming",
        "Guiyang",
        "Chengdu",
        "Chongqing",
        "Wuhan",
        "Changsha",
        "Nanchang",
        "Fuzhou",
        "Xiamen",
        "Hangzhou",
        "Ningbo",
        "Shanghai",
        "Suzhou",
        "Nanjing",
        "Hefei",
        "Zhengzhou",
        "Xi'an",
        "Xian",
        "Lanzhou",
        "Xining",
        "Yinchuan",
        "Urumqi",
        "Lhasa",
        "Harbin",
        "Changchun",
        "Shenyang",
        "Dalian",
        "Qingdao",
        "Jinan",
        "Tianjin",
        "Beijing",
        "Shijiazhuang",
        "Taiyuan",
        "Hohhot",
        "Hong Kong",
        "Macau",
        "Taipei",
    ]

    results = []
    for city in cities:
        try:
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": api_key, "units": "metric", "lang": "zh_cn"},
                timeout=8,
            )
            if response.status_code != 200:
                print(f"{city} | 查询失败 | HTTP {response.status_code}")
                continue

            payload = response.json()
        except requests.RequestException as exc:
            print(f"{city} | 查询失败 | {type(exc).__name__}")
            continue

        rainfall = rainfall_from_payload(payload)
        description = (payload.get("weather") or [{}])[0].get("description", "无描述")
        api_city_name = payload.get("name", city)
        results.append((city, api_city_name, rainfall, description))
        time.sleep(0.15)

    rainy = [item for item in results if item[2] > 0]
    rainy.sort(key=lambda item: item[2], reverse=True)
    results.sort(key=lambda item: item[2], reverse=True)

    print("当前有降雨的城市：")
    if rainy:
        for city, api_city_name, rainfall, description in rainy:
            print(f"{city} | {api_city_name} | {rainfall:.1f} mm/h | {description}")
    else:
        print("这批城市当前都没有返回 rain 字段。")

    print("\n降雨强度排名前 12：")
    for city, api_city_name, rainfall, description in results[:12]:
        print(f"{city} | {api_city_name} | {rainfall:.1f} mm/h | {description}")


if __name__ == "__main__":
    main()
