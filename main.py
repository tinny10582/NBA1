import requests
import pandas as pd

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"


# ===============================
# 📊 球隊數據
# ===============================
team_stats = {
    "Lakers": {"off":115,"def":112,"home":1.05},
    "Warriors": {"off":118,"def":115,"home":1.06},
    "Celtics": {"off":117,"def":110,"home":1.07},
    "Bucks": {"off":116,"def":111,"home":1.05},
    "Nuggets": {"off":117,"def":112,"home":1.06},
    "Heat": {"off":110,"def":108,"home":1.04},
    "Suns": {"off":116,"def":113,"home":1.05},
    "Clippers": {"off":114,"def":111,"home":1.05},
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
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    return res.json()

# ===============================
# 🧠 預測
# ===============================
def predict(home, away):

    A = team_stats.get(home, {"off":112,"def":112,"home":1})
    B = team_stats.get(away, {"off":112,"def":112,"home":1})

    sh = (A["off"] + B["def"]) / 2
    sa = (B["off"] + A["def"]) / 2

    sh *= A["home"]

    total = sh + sa
    diff = sh - sa

    prob = 0.5 + diff / 25

    return total, diff, prob

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

        home = g["home_team"]
        away = g["away_team"]

        total, diff, prob = predict(home, away)

        winner = home if diff > 0 else away
        ou = "大分" if total > 215 else "小分"

        results.append({
            "match": f"{away} vs {home}",
            "winner": winner,
            "ou": ou,
            "prob": prob,
            "star": star(prob)
        })

    df = pd.DataFrame(results).sort_values(by="prob", ascending=False)

    # ===============================
    # 📊 全場分析
    # ===============================
    msg = "🔥【NBA全場預測】🔥\n━━━━━━━━━━\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n"
        msg += f"👉 勝負: {r['winner']}\n"
        msg += f"👉 {r['ou']}\n"
        msg += f"勝率:{round(r['prob']*100,1)}% {r['star']}\n\n"

    # ===============================
    # 🔥 高勝率組合
    # ===============================
    msg += "━━━━━━━━━━\n🔥高勝率推薦組合\n"

    top2 = df.head(2)
    top3 = df.head(3)

    msg += "\n👉 串2關\n"
    for _, r in top2.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n👉 串3關\n"
    for _, r in top3.iterrows():
        msg += f"{r['winner']}（{r['match']}）\n"

    msg += "\n━━━━━━━━━━\n⚠️ 挑星星多的優先下注"

    send(msg)

# ===============================
if __name__ == "__main__":
    main()
