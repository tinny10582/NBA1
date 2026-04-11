
import requests
import pandas as pd
import json
import os
import datetime

print("🔥 NBA系統啟動")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"


PREDICT_FILE = "predict.json"

# ===============================
# 🌏 中文隊名
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

# ===============================
# 📲 Discord
# ===============================
def send(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        print("❌ Discord失敗")

# ===============================
# 🌍 抓盤
# ===============================
def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    
    res = requests.get(url)

    if res.status_code != 200:
        return []

    data = res.json()

    if isinstance(data, dict):
        return []

    return data

# ===============================
# 🧠 分析
# ===============================
def analyze(data):

    results = []

    for g in data:

        try:
            home = g["home_team"]
            away = g["away_team"]

            spread = None
            total = None

            for b in g.get("bookmakers", []):
                for m in b.get("markets", []):

                    if m["key"] == "spreads":
                        for o in m["outcomes"]:
                            if o["name"] == home:
                                spread = o["point"]

                    if m["key"] == "totals":
                        total = m["outcomes"][0]["point"]

            if spread is None or total is None:
                continue

            # 👉 台彩模擬
            spread_tw = spread - 1.5
            total_tw = total + 2

            # 👉 推薦
            if spread_tw <= -8:
                pick = away
                prob = 0.65
            elif spread_tw >= 8:
                pick = home
                prob = 0.65
            else:
                pick = home if spread < 0 else away
                prob = 0.55

            # 👉 大小
            if total_tw >= 230:
                ou = "小分"
            elif total_tw <= 210:
                ou = "大分"
            else:
                ou = "小分"

            results.append({
                "match": f"{team_zh.get(away,away)} vs {team_zh.get(home,home)}",
                "pick": team_zh.get(pick,pick),
                "prob": prob,
                "ou": ou
            })

        except:
            continue

    return pd.DataFrame(results)

# ===============================
# 💾 存預測
# ===============================
def save_predictions(df):
    df.to_json(PREDICT_FILE, orient="records", force_ascii=False)

def load_predictions():
    if not os.path.exists(PREDICT_FILE):
        return pd.DataFrame()
    return pd.read_json(PREDICT_FILE)

# ===============================
# 📊 抓比分
# ===============================
def get_results():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={ODDS_API_KEY}&daysFrom=1"
    
    res = requests.get(url)

    if res.status_code != 200:
        return []

    data = res.json()

    if isinstance(data, dict):
        return []

    return data

# ===============================
# 🧾 驗證
# ===============================
def check_results():

    preds = load_predictions()

    if preds.empty:
        send("❌ 沒有預測紀錄")
        return

    results_api = get_results()

    win = 0
    lose = 0

    msg = "📊【昨日預測結果】\n━━━━━━━━━━\n\n"

    for _, p in preds.iterrows():

        match = p["match"]
        pick = p["pick"]

        for g in results_api:

            home = g["home_team"]
            away = g["away_team"]

            match_api = f"{team_zh.get(away,away)} vs {team_zh.get(home,home)}"

            if match_api == match:

                home_score = g.get("scores", [{}])[0].get("score")
                away_score = g.get("scores", [{}])[1].get("score")

                if home_score is None:
                    continue

                winner = home if int(home_score) > int(away_score) else away
                winner_zh = team_zh.get(winner,winner)

                if winner_zh == pick:
                    msg += f"✔ {match} 命中\n"
                    win += 1
                else:
                    msg += f"❌ {match} 失敗\n"
                    lose += 1

    total = win + lose
    rate = round(win / total * 100, 1) if total > 0 else 0

    msg += f"\n━━━━━━━━━━\n🎯 命中率：{rate}% ({win}/{total})"

    send(msg)

# ===============================
# 🚀 主程式
# ===============================
def main():

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    hour = now.hour

    print("目前時間:", hour)

    # 👉 晚上6點 驗證
    if hour == 18:
        check_results()
        return

    # 👉 其他時間 預測
    data = get_games()

    if len(data) == 0:
        send("❌ 今日無比賽")
        return

    df = analyze(data)

    if df.empty:
        send("❌ 無分析結果")
        return

    save_predictions(df)

    msg = "🔥【NBA今日預測】🔥\n━━━━━━━━━━\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n👉 {r['pick']}\n👉 {r['ou']}\n\n"

    send(msg)

# ===============================
if __name__ == "__main__":
    main()
