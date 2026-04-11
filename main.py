
import requests
import pandas as pd
import time

# 👉 開關（重點）
USE_REAL_TAIWAN = False   # True=抓台彩 / False=用國際盤

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"


# ===============================
# 🌏 NBA 30隊完整中文
# ===============================
team_zh = {
    "Atlanta Hawks":"老鷹","Boston Celtics":"塞爾提克","Brooklyn Nets":"籃網",
    "Charlotte Hornets":"黃蜂","Chicago Bulls":"公牛","Cleveland Cavaliers":"騎士",
    "Dallas Mavericks":"獨行俠","Denver Nuggets":"金塊","Detroit Pistons":"活塞",
    "Golden State Warriors":"勇士","Houston Rockets":"火箭","Indiana Pacers":"溜馬",
    "Los Angeles Clippers":"快艇","Los Angeles Lakers":"湖人","Memphis Grizzlies":"灰熊",
    "Miami Heat":"熱火","Milwaukee Bucks":"公鹿","Minnesota Timberwolves":"灰狼",
    "New Orleans Pelicans":"鵜鶘","New York Knicks":"尼克","Oklahoma City Thunder":"雷霆",
    "Orlando Magic":"魔術","Philadelphia 76ers":"76人","Phoenix Suns":"太陽",
    "Portland Trail Blazers":"拓荒者","Sacramento Kings":"國王","San Antonio Spurs":"馬刺",
    "Toronto Raptors":"暴龍","Utah Jazz":"爵士","Washington Wizards":"巫師"
}

def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 🌍 國際盤
# ===============================
def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return r.json()

# ===============================
# 🇹🇼 真台彩（手動模式用）
# ===============================
def get_real_taiwan():
    print("⚠️ 這裡需 Selenium（僅本地用）")
    return []

# ===============================
# 🧠 分析
# ===============================
def analyze(data):

    results = []

    for g in data:

        home = g["home_team"]
        away = g["away_team"]

        spread = None
        total = None

        try:
            for b in g["bookmakers"]:
                for m in b["markets"]:

                    if m["key"] == "spreads":
                        for o in m["outcomes"]:
                            if o["name"] == home:
                                spread = o["point"]

                    if m["key"] == "totals":
                        total = m["outcomes"][0]["point"]
        except:
            continue

        if spread is None or total is None:
            continue

        # =========================
        # 🔥 動態大小分（修正你問題）
        # =========================

        if total >= 230:
            ou = "小分（超高盤）"
        elif total >= 222:
            ou = "小分（高盤）"
        elif total <= 210:
            ou = "大分（低盤）"
        else:
            ou = "中性偏小"

        # =========================
        # 🔥 讓分
        # =========================
        if spread <= -8:
            pick = away
            prob = 0.65
        elif spread >= 8:
            pick = home
            prob = 0.65
        else:
            pick = home if spread < 0 else away
            prob = 0.55

        results.append({
            "match": f"{team_zh.get(away,away)} vs {team_zh.get(home,home)}",
            "pick": team_zh.get(pick,pick),
            "ou": ou,
            "prob": prob
        })

    return pd.DataFrame(results)

# ===============================
# 🚀 主程式
# ===============================
def main():

    print("🔥 系統啟動")

    data = get_games()

    if not data:
        send("❌ 無資料")
        return

    df = analyze(data)

    if df.empty:
        send("❌ 無分析")
        return

    df = df.sort_values(by="prob", ascending=False)

    msg = "🔥【NBA台彩邏輯版】🔥\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n👉 {r['pick']} | {r['ou']}\n勝率:{round(r['prob']*100)}%\n\n"

    msg += "🔥串2\n"
    for _, r in df.head(2).iterrows():
        msg += f"{r['pick']} + "

    send(msg)

if __name__ == "__main__":
    main()
