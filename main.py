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
}

# ===============================
# 📲 Discord
# ===============================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ===============================
# 📊 Odds API
# ===============================
def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=spreads,totals,h2h"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    return res.json()

# ===============================
# 🤕 ESPN 傷兵
# ===============================
def get_injuries(team):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        data = requests.get(url).json()

        for t in data["sports"][0]["leagues"][0]["teams"]:
            if t["team"]["displayName"] == team:
                injuries = t["team"].get("injuries", [])
                return -len(injuries)
    except:
        return 0

    return 0

# ===============================
# 🧠 預測模型
# ===============================
def predict(home, away):

    A = team_stats.get(home, {"off":112,"def":112,"home":1})
    B = team_stats.get(away, {"off":112,"def":112,"home":1})

    injA = get_injuries(home)
    injB = get_injuries(away)

    sh = (A["off"] + B["def"]) / 2 + injA
    sa = (B["off"] + A["def"]) / 2 + injB

    sh *= A["home"]

    total = sh + sa
    diff = sh - sa

    prob = 0.5 + (diff / 25)

    return total, diff, prob

# ===============================
# 💰 EV + Kelly
# ===============================
def calc_ev(prob, odds):
    return (prob * odds) - 1

def kelly(prob, odds):
    b = odds - 1
    return max((prob * b - (1 - prob)) / b, 0)

# ===============================
# ⭐ 信心
# ===============================
def star(prob, ev):
    if prob > 0.65 and ev > 0.08:
        return 3
    elif prob > 0.58 and ev > 0.05:
        return 2
    else:
        return 1

# ===============================
# 🚀 主程式
# ===============================
def main():

    games = get_games()

    if len(games) == 0:
        send("❌ 無比賽")
        return

    results = []

    for g in games:

        home = g["home_team"]
        away = g["away_team"]

        total, diff, prob = predict(home, away)

        spread = 0
        odds = 1.9  # 台彩近似

        try:
            for book in g["bookmakers"]:
                for m in book["markets"]:
                    if m["key"] == "spreads":
                        spread = m["outcomes"][0]["point"]
        except:
            pass

        pick = home if diff > spread else away

        ev = calc_ev(prob, odds)

        # ❗只下注 EV > 5%
        if ev < 0.05:
            continue

        k = kelly(prob, odds)

        s = star(prob, ev)

        results.append({
            "match": f"{away} vs {home}",
            "pick": pick,
            "prob": prob,
            "ev": ev,
            "kelly": k,
            "star": s
        })

    if len(results) < 2:
        send("❌ 無EV下注場")
        return

    df = pd.DataFrame(results).sort_values(by=["star","ev"], ascending=False)

    msg = "🔥【NBA職業最終版】🔥\n━━━━━━━━━━\n\n"

    for s in [3,2,1]:
        sub = df[df["star"] == s]
        if len(sub) > 0:
            msg += f"⭐{s}星\n"
            for _, r in sub.iterrows():
                msg += f"{r['match']}\n👉 {r['pick']}\n勝率:{round(r['prob']*100,1)}%\nEV:{round(r['ev']*100,1)}%\nKelly:{round(r['kelly']*100,1)}%\n\n"

    # ===============================
    # 🔗 串關最佳化（3關）
    # ===============================
    msg += "━━━━━━━━━━\n🔥串3關最佳\n"

    picks = df.head(3)

    for _, r in picks.iterrows():
        msg += f"👉 {r['pick']}（{r['match']}）\n"

    msg += "━━━━━━━━━━\n⚠️ EV > 5% 才下注"

    send(msg)

# ===============================
if __name__ == "__main__":
    main()
