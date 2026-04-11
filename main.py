import requests
import pandas as pd

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"

# ===============================
# 📲 發送
# ===============================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 📊 抓賽事
# ===============================
def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=spreads,totals"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    return res.json()

# ===============================
# 🧠 用盤口算勝率（關鍵）
# ===============================
def predict(game):

    home = game["home_team"]
    away = game["away_team"]

    spread = None
    total_line = None

    try:
        for book in game["bookmakers"]:
            for m in book["markets"]:

                # 讓分
                if m["key"] == "spreads":
                    for o in m["outcomes"]:
                        if o["name"] == home:
                            spread = o["point"]

                # 大小分
                if m["key"] == "totals":
                    total_line = m["outcomes"][0]["point"]

    except:
        pass

    # 沒抓到盤口就跳過
    if spread is None:
        return None

    # 👉 核心：讓分轉勝率
    prob = 0.5 + (-spread / 14)

    prob = max(min(prob, 0.75), 0.25)

    # 勝負
    winner = home if spread < 0 else away

    # 大小分
    ou = "大分" if total_line and total_line > 215 else "小分"

    return winner, ou, prob

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

        winner, ou, prob = res

        results.append({
            "match": f"{g['away_team']} vs {g['home_team']}",
            "winner": winner,
            "ou": ou,
            "prob": prob,
            "star": star(prob)
        })

    df = pd.DataFrame(results).sort_values(by="prob", ascending=False)

    # ===============================
    # 📊 全場分析（中文）
    # ===============================
    msg = "🔥【NBA盤口分析（台彩用）】🔥\n━━━━━━━━━━\n\n"

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

    msg += "\n👉 串2關\n"
    for _, r in top2.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n👉 串3關\n"
    for _, r in top3.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n━━━━━━━━━━\n⚠️ 優先選 ⭐⭐⭐"

    send(msg)

# ===============================
if __name__ == "__main__":
    main()
