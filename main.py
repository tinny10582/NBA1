import requests
import pandas as pd

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"


# ===============================
# 📊 球隊強度（含主場）
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
# 🤕 傷兵影響（簡化版）
# ===============================
injury_factor = {
    "Lakers": -2,
    "Warriors": -1,
    "Celtics": 0,
    "Bucks": -1,
    "Nuggets": 0,
}

# ===============================
# 📲 發送Discord
# ===============================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 📊 抓賠率（含讓分）
# ===============================
def get_games():

    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=spreads,totals"

    res = requests.get(url)

    if res.status_code != 200:
        print("API錯誤:", res.status_code)
        return []

    return res.json()

# ===============================
# 🧠 模型（升級）
# ===============================
def predict(home, away):

    A = team_stats.get(home, {"off":112,"def":112,"home":1})
    B = team_stats.get(away, {"off":112,"def":112,"home":1})

    injA = injury_factor.get(home, 0)
    injB = injury_factor.get(away, 0)

    # 基礎分數
    sh = (A["off"] + B["def"]) / 2 + injA
    sa = (B["off"] + A["def"]) / 2 + injB

    # 主場加成
    sh *= A["home"]

    total = sh + sa
    diff = sh - sa

    prob = 0.5 + (diff / 28)

    return total, diff, prob

# ===============================
# ⭐ 信心
# ===============================
def star(prob):
    if prob >= 0.63:
        return 3
    elif prob >= 0.57:
        return 2
    else:
        return 1

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

        # ❗ 過濾低勝率（關鍵）
        if prob < 0.55:
            continue

        pick = home if diff > 0 else away
        ou = "大分" if total > 215 else "小分"

        results.append({
            "match": f"{away} vs {home}",
            "pick": pick,
            "ou": ou,
            "prob": prob,
            "star": star(prob)
        })

    if len(results) < 2:
        send("❌ 沒有高勝率場")
        return

    df = pd.DataFrame(results).sort_values(by=["star","prob"], ascending=False)

    # ===============================
    # 📊 輸出分析
    # ===============================
    msg = "🔥【NBA職業分析】🔥\n━━━━━━━━━━\n\n"

    for s in [3,2,1]:
        sub = df[df["star"] == s]
        if len(sub) > 0:
            msg += f"⭐{s}星（信心）\n"
            for _, r in sub.iterrows():
                msg += f"{r['match']}\n👉 勝負: {r['pick']}\n👉 {r['ou']}\n勝率:{round(r['prob']*100,1)}%\n\n"

    # ===============================
    # 🔗 串2關（台彩）
    # ===============================
    msg += "━━━━━━━━━━\n🔥台彩串2關\n"

    a = df.iloc[0]
    b = df.iloc[1]

    msg += f"\n👉 {a['pick']}（{a['match']}）"
    msg += f"\n👉 {b['pick']}（{b['match']}）"

    msg += "\n━━━━━━━━━━\n⚠️ 只下注高信心"

    send(msg)

# ===============================
# ▶️ 執行
# ===============================
if __name__ == "__main__":
    main()
