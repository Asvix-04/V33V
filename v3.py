import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


# Delhi coordinates
DELHI_LAT = 28.6139
DELHI_LON = 77.2090

USER_TRIGGERS = {
    "dust": True,
    "smoke": True,
    "strong_perfumes": True,
    "running": True
}

# -------------------------
# Data Fetchers
# -------------------------

def get_weather():
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={DELHI_LAT}&lon={DELHI_LON}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        print("⚠️ Weather API response not ready yet:")
        print(data)
        return {}

    return data

def get_aqi():
    url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={DELHI_LAT}&lon={DELHI_LON}&appid={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "list" not in data:
        print("⚠️ AQI API response not ready yet:")
        print(data)
        return None

    return data

# -------------------------
# Risk Scoring Logic
# -------------------------

def calculate_risk(weather, aqi):
    risk = 0
    reasons = []

    # ---- SAFE WEATHER ACCESS ----
    humidity = weather.get("main", {}).get("humidity", 0)
    temp = weather.get("main", {}).get("temp", 0)

    # ---- SAFE AQI ACCESS ----
    pm25 = 0
    if aqi and isinstance(aqi, dict):
        try:
            pm25 = aqi["list"][0]["components"].get("pm2_5", 0)
        except (KeyError, IndexError, TypeError):
            pm25 = 0

    # ---- POLLUTION LOGIC ----
    if pm25 > 60:
        risk += 40
        reasons.append("Very high PM2.5 (pollution)")
    elif pm25 > 35:
        risk += 25
        reasons.append("Moderate PM2.5 levels")

    # ---- HUMIDITY ----
    if humidity > 70:
        risk += 15
        reasons.append("High humidity")

    # ---- COLD AIR ----
    if temp < 15:
        risk += 10
        reasons.append("Cold air exposure risk")

    # ---- PERSONAL TRIGGERS ----
    if USER_TRIGGERS.get("dust") or USER_TRIGGERS.get("smoke"):
        risk *= 1.2

    if USER_TRIGGERS.get("running"):
        risk *= 1.15
        reasons.append("Outdoor exertion increases inhalation")

    return min(int(risk), 100), reasons

# -------------------------
# Recommendation Engine
# -------------------------

def recommendations(risk):
    if risk < 30:
        return [
            "Outdoor activity is generally safe",
            "Carry inhaler as precaution"
        ]

    if 30 <= risk < 60:
        return [
            "Limit outdoor exposure",
            "Avoid running outdoors",
            "Wear a mask if stepping out",
            "Drink warm fluids"
        ]

    return [
        "Avoid outdoor activity",
        "Wear a mask if unavoidable",
        "Avoid exercise",
        "Keep rescue inhaler accessible",
        "Stay indoors with windows closed"
    ]

# -------------------------
# Main Runner
# -------------------------

def run_v3():
    weather = get_weather()
    aqi = get_aqi()

    risk, reasons = calculate_risk(weather, aqi)

    # ---- SAFE WEATHER READ ----
    temp = weather.get("main", {}).get("temp", "N/A")
    humidity = weather.get("main", {}).get("humidity", "N/A")

    # ---- SAFE AQI READ ----
    pm25 = "N/A"
    if aqi and isinstance(aqi, dict):
        try:
            pm25 = aqi["list"][0]["components"].get("pm2_5", "N/A")
        except (KeyError, IndexError, TypeError):
            pm25 = "N/A"

    print("\n===== V3 | Asthma Risk Check (Delhi) =====")
    print(f"Temperature: {temp} °C")
    print(f"Humidity: {humidity} %")
    print(f"PM2.5: {pm25} µg/m³")

    print(f"\nRisk Score: {risk}/100")

    if reasons:
        print("\nWhy:")
        for r in reasons:
            print(f"- {r}")
    else:
        print("\nWhy:")
        print("- Limited data available, conservative estimate applied")

    print("\nWhat to do:")
    for a in recommendations(risk):
        print(f"- {a}")

    if risk >= 60:
        print("\n🚫 Recommendation: Avoid roaming in Delhi right now.")
    else:
        print("\n✅ Recommendation: You may step out with precautions.")

if __name__ == "__main__":
    run_v3()
