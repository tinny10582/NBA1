


import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"

# ===============================
# 🌏 中文翻譯
# ===============================
team_zh = {
    "Cleveland Cavaliers": "騎士",
    "Atlanta Hawks": "老鷹",
    "Boston Celtics": "塞爾提克",
    "New York Knicks": "尼克",
    "Toronto Raptors": "暴龍",
    "Milwaukee Bucks": "公鹿",
    "Miami Heat": "熱火",
    "Chicago Bulls": "公牛",
    "Los Angeles Lakers": "湖人",
    "Golden State Warriors": "勇士",
    "Phoenix Suns": "太陽",
    "Denver Nuggets": "金塊",
    "Dallas Mavericks": "獨行俠",
    "Brooklyn Nets": "籃網",
    "Memphis Grizzlies": "灰熊",
    "Utah Jazz": "爵士",
    "Houston Rockets": "火箭",
    "San Antonio Spurs": "馬刺",
    "Oklahoma City Thunder": "雷霆",
    "Orlando Magic": "魔術",
    "Detroit Pistons": "活塞",
    "Charlotte Hornets": "黃蜂",
    "Indiana Pacers": "溜馬",
    "Washington Wizards": "巫師",
    "Sacramento Kings": "國王",
    "Portland Trail Blazers": "拓荒者",
    "Los Angeles Clippers": "快艇",
    "Minnesota Timberwolves": "灰狼",
    "New Orleans Pelicans": "鵜鶘"
}



# ===============================
# 🌏 中文翻譯
# ===============================
team_zh = {
    "Cleveland Cavaliers": "騎士",
    "Atlanta Hawks": "老鷹",
    "Boston Celtics": "塞爾提克",
    "New York Knicks": "尼克",
    "Toronto Raptors": "暴龍",
    "Milwaukee Bucks": "公鹿",
    "Miami Heat": "熱火",
    "Chicago Bulls": "公牛",
    "Los Angeles Lakers": "湖人",
    "Golden State Warriors": "勇士",
    "Phoenix Suns": "太陽",
    "Denver Nuggets": "金塊",
    "Dallas Mavericks": "獨行俠",
    "Brooklyn Nets": "籃網",
    "Memphis Grizzlies": "灰熊",
    "Utah Jazz": "爵士",
    "Houston Rockets": "火箭",
    "San Antonio Spurs": "馬刺",
    "Oklahoma City Thunder": "雷霆",
    "Orlando Magic": "魔術",
    "Detroit Pistons": "活塞",
    "Charlotte Hornets": "黃蜂",
    "Indiana Pacers": "溜馬",
    "Washington Wizards": "巫師",
    "Sacramento Kings": "國王",
    "Portland Trail Blazers": "拓荒者",
    "Los Angeles Clippers": "快艇",
    "Minnesota Timberwolves": "灰狼",
    "New Orleans Pelicans": "鵜鶘"
}


# ===============================
# 📲 Discord
# ===============================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 🌍 國際盤
# ===============================
def get_global():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals,h2h"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    return res.json()

# ===============================
# 🇹🇼 Selenium抓台彩
# ===============================
def get_taiwan():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.get("https://www.sportslottery.com.tw")

    time.sleep(5)

    games = []

    try:
        matches = driver.find_elements(By.CLASS_NAME, "match")

        for m in matches:

            teams = m.find_elements(By.CLASS_NAME, "team")
            odds = m.find_elements(By.CLASS_NAME, "odds")

            home = teams[1].text
            away = teams[0].text

            spread = float(odds[0].text)
            total = float(odds[1].text)

            games.append({
                "home": home,
                "away": away,
                "spread": spread,
                "total": total
            })

    except Exception as e:
        print("台彩解析錯:", e)

    driver.quit()
    return games

# ===============================
# 🧠 比對套利
# ===============================
def analyze(tw, global_data):

    results = []

    for g in tw:

        home = g["home"]
        away = g["away"]

        spread_tw = g["spread"]
        total_tw = g["total"]

        # 👉 找國際盤
        spread_g = None

        for gd in global_data:
            if home in gd["home_team"]:

                for b in gd["bookmakers"]:
                    for m in b["markets"]:
                        if m["key"] == "spreads":
                            for o in m["outcomes"]:
                                if o["name"] == gd["home_team"]:
                                    spread_g = o["point"]

        if spread_g is None:
            continue

        # =====================
        # 🔥 核心套利
        # =====================

        diff = spread_tw - spread_g

        if diff <= -2:
            pick = away
            prob = 0.65
        elif diff >= 2:
            pick = home
            prob = 0.65
        else:
            pick = home
            prob = 0.55

        # 👉 大小
        if total_tw > 228:
            ou = "小分"
        elif total_tw < 215:
            ou = "大分"
        else:
            ou = "小分"

        results.append({
            "match": f"{away} vs {home}",
            "pick": pick,
            "ou": ou,
            "prob": prob
        })

    return pd.DataFrame(results)

# ===============================
# 🚀 主程式
# ===============================
def main():

    print("🔥 系統啟動")

    tw = get_taiwan()
    global_data = get_global()

    if len(tw) == 0:
        send("❌ 台彩抓不到")
        return

    df = analyze(tw, global_data)

    if df.empty:
        send("❌ 無結果")
        return

    df = df.sort_values(by="prob", ascending=False)

    msg = "🔥【台彩套利版】🔥\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n"
        msg += f"👉 {r['pick']}\n"
        msg += f"👉 {r['ou']}\n"
        msg += f"👉 勝率:{round(r['prob']*100)}%\n\n"

    msg += "🔥串2\n"
    for _, r in df.head(2).iterrows():
        msg += f"{r['pick']} + "

    send(msg)

if __name__ == "__main__":
    main()

