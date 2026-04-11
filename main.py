import requests
import pandas as pd

print("🔥 程式啟動成功")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"

team_stats = {
    "Lakers": {"off":115,"def":112,"pace":100},
    "Warriors": {"off":118,"def":115,"pace":102},
    "Celtics": {"off":117,"def":110,"pace":99},
    "Bucks": {"off":116,"def":111,"pace":101},
    "Nuggets": {"off":117,"def":112,"pace":98},
}

def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    res = requests.get(url)

    if res.status_code != 200:
        print("API錯誤:", res.status_code)
        return []

    return res.json()

def predict(home, away):

    A = team_stats.get(home, {"off":112,"def":112,"pace":100})
    B = team_stats.get(away, {"off":112,"def":112,"pace":100})

    pace = (A["pace"] + B["pace"]) / 200

    sh = (A["off"] + B["def"]) / 2 * pace
    sa = (B["off"] + A["def"]) / 2 * pace

    total = sh + sa
    diff = sh - sa
    prob = 0.5 + diff / 40

    return total, prob

def star(prob):
    if prob >= 0.60:
        return 3
    elif prob >= 0.56:
        return 2
    else:
        return 1

def main():

    games = get_odds()

    if len(games) == 0:
        send("❌ 沒有比賽")
        return

    results = []

    for g in games:

        home = g["home_team"]
        away = g["away_team"]

        total, prob = predict(home, away)

        pick = "大分" if total > 215 else "小分"
        s = star(prob)

        results.append({
            "match": f"{away} vs {home}",
            "pick": pick,
            "prob": prob,
            "star": s
        })

    df = pd.DataFrame(results).sort_values(by=["star","prob"], ascending=False)

    msg = "🔥【NBA進階分析】🔥\n━━━━━━━━━━\n\n"

    for s in [3,2,1]:
        sub = df[df["star"] == s]
        if len(sub) > 0:
            msg += f"⭐{s}星\n"
            for _, r in sub.iterrows():
                msg += f"{r['match']}\n👉 {r['pick']}\n勝率:{round(r['prob']*100,1)}%\n\n"

    msg += "━━━━━━━━━━\n🔥串2關推薦\n"

    if len(df) >= 2:
        a = df.iloc[0]
        b = df.iloc[1]

        msg += f"\n👉 {a['pick']}（{a['match']}）"
        msg += f"\n👉 {b['pick']}（{b['match']}）"

    msg += "\n━━━━━━━━━━\n⚠️ 由高星開始下注"

    send(msg)

if __name__ == "__main__":
    main()
