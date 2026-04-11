import requests
import pandas as pd

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
# 📲 Discord
# ===============================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 📊 抓比賽
# ===============================
def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=spreads,totals"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    return res.json()

# ===============================
# 🧠 用盤口算勝率
# ===============================
def predict(game):

    home = game["home_team"]
    away = game["away_team"]

    spread = None
    total_line = None

    try:
        for book in game["bookmakers"]:
            for m in book["markets"]:

                if m["key"] == "spreads":
                    for o in m["outcomes"]:
                        if o["name"] == home:
                            spread = o["point"]

                if m["key"] == "totals":
                    total_line = m["outcomes"][0]["point"]

    except:
        pass

    if spread is None:
        return None

    # 👉 讓分轉勝率（核心）
    prob = 0.5 + (-spread / 14)
    prob = max(min(prob, 0.75), 0.25)

    # 👉 推薦隊
    winner_en = home if spread < 0 else away
    winner = team_zh.get(winner_en, winner_en)

    # 👉 中文隊名
    home_zh = team_zh.get(home, home)
    away_zh = team_zh.get(away, away)

    # 👉 大小分
    ou = "大分（進攻盤）" if total_line and total_line > 215 else "小分（防守盤）"

    return f"{away_zh} vs {home_zh}", winner, ou, prob

# ===============================
# ⭐ 信心
# ===============================
def star(prob):
    if prob >= 0.65:
        return "⭐⭐⭐"
    elif prob >= 0.58:
        return "⭐⭐"
    else:
        return "⭐"

# ===============================
# 🚀 主程式
# ===============================
def main():

    games = get_games()

    if len(games) == 0:
        send("❌ 今日無比賽")
        return

    results = []

    for g in games:

        res = predict(g)

        if res is None:
            continue

        match, winner, ou, prob = res

        results.append({
            "match": match,
            "winner": winner,
            "ou": ou,
            "prob": prob,
            "star": star(prob)
        })

    df = pd.DataFrame(results).sort_values(by="prob", ascending=False)

    # ===============================
    # 📊 全場分析
    # ===============================
    msg = "🔥【NBA預測（台彩版）】🔥\n━━━━━━━━━━\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n"
        msg += f"👉 推薦：{r['winner']}\n"
        msg += f"👉 大小分：{r['ou']}\n"
        msg += f"👉 勝率：約 {round(r['prob']*100,1)}% {r['star']}\n\n"

    # ===============================
    # 🔥 高勝率組合
    # ===============================
    msg += "━━━━━━━━━━\n🔥高勝率組合\n"

    top2 = df.head(2)
    top3 = df.head(3)

    msg += "\n👉 串2關（台彩建議）\n"
    for _, r in top2.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n👉 串3關（進階）\n"
    for _, r in top3.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n━━━━━━━━━━\n⚠️ 優先選 ⭐⭐⭐（高信心）"

    send(msg)

# ===============================
if __name__ == "__main__":
    main()
