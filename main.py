import requests
import pandas as pd

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"

def send(msg):
    r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
    print("Discord狀態:", r.status_code)

def main():
    print("🔥 main執行")

    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    res = requests.get(url)

    print("API狀態:", res.status_code)

    if res.status_code != 200:
        send("❌ API錯誤")
        return

    data = res.json()

    if len(data) == 0:
        send("❌ 今日無比賽")
        return

    msg = "🔥 NBA今日推薦 🔥\n\n"

    for game in data[:5]:
        msg += f"{game['away_team']} vs {game['home_team']}\n"

    send(msg)

    print("🔥 發送完成")


if __name__ == "__main__":
    main()
