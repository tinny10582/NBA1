import requests
import pandas as pd
import os
import datetime

print("🔥 系統啟動")

ODDS_API_KEY = "你的API"
DISCORD_WEBHOOK = "你的WEBHOOK"

PREDICT_FILE = "predict.json"

# ===============================
# 🌏 NBA中文
# ===============================
nba_zh = {
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
# 🌏 MLB中文（完整）
# ===============================
mlb_zh = {
    "Arizona Diamondbacks": "響尾蛇","Atlanta Braves": "勇士","Baltimore Orioles": "金鶯",
    "Boston Red Sox": "紅襪","Chicago Cubs": "小熊","Chicago White Sox": "白襪",
    "Cincinnati Reds": "紅人","Cleveland Guardians": "守護者","Colorado Rockies": "洛磯",
    "Detroit Tigers": "老虎","Houston Astros": "太空人","Kansas City Royals": "皇家",
    "Los Angeles Angels": "天使","Los Angeles Dodgers": "道奇","Miami Marlins": "馬林魚",
    "Milwaukee Brewers": "釀酒人","Minnesota Twins": "雙城","New York Mets": "大都會",
    "New York Yankees": "洋基","Oakland Athletics": "運動家","Philadelphia Phillies": "費城人",
    "Pittsburgh Pirates": "海盜","San Diego Padres": "教士","San Francisco Giants": "巨人",
    "Seattle Mariners": "水手","St. Louis Cardinals": "紅雀","Tampa Bay Rays": "光芒",
    "Texas Rangers": "遊騎兵","Toronto Blue Jays": "藍鳥","Washington Nationals": "國民"
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
# 🌍 API
# ===============================
def get_nba():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

def get_mlb():
    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# ===============================
# 🧠 勝率模型
# ===============================
def winrate_spread(s):
    s = abs(s)
    if s >= 11: return 0.72
    elif s >= 9: return 0.67
    elif s >= 7: return 0.63
    elif s >= 5: return 0.58
    elif s >= 3: return 0.54
    else: return 0.50

def winrate_total(t):
    if t >= 235: return ("小分", 0.63)
    elif t <= 210: return ("大分", 0.62)
    else: return ("略過", 0.50)

def star(p):
    if p >= 0.65: return "⭐⭐⭐"
    elif p >= 0.60: return "⭐⭐"
    else: return "⭐"

# ===============================
# 🧠 NBA分析
# ===============================
def analyze_nba(data):

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

            sp_rate = winrate_spread(spread)
            ou_pick, ou_rate = winrate_total(total)

            if sp_rate >= ou_rate:
                pick = home if spread < 0 else away
                prob = sp_rate
                bet = "讓分"
            else:
                pick = ou_pick
                prob = ou_rate
                bet = "大小分"

            results.append({
                "match": f"{nba_zh.get(away,away)} vs {nba_zh.get(home,home)}",
                "pick": nba_zh.get(pick,pick),
                "bet": bet,
                "prob": prob,
                "star": star(prob)
            })

        except:
            continue

    return pd.DataFrame(results)

# ===============================
# 🧠 MLB分析
# ===============================
def analyze_mlb(data):

    results = []

    for g in data:
        try:
            home = g["home_team"]
            away = g["away_team"]

            total = None

            for b in g.get("bookmakers", []):
                for m in b.get("markets", []):
                    if m["key"] == "totals":
                        total = m["outcomes"][0]["point"]

            if total is None:
                continue

            if total >= 9:
                pick = "小分"
                prob = 0.62
            elif total <= 7:
                pick = "大分"
                prob = 0.61
            else:
                continue

            results.append({
                "match": f"{mlb_zh.get(away,away)} vs {mlb_zh.get(home,home)}",
                "pick": pick,
                "bet": "大小分",
                "prob": prob,
                "star": star(prob)
            })

        except:
            continue

    return pd.DataFrame(results)

# ===============================
# 💾 存NBA預測
# ===============================
def save_predictions(df):
    df.to_json(PREDICT_FILE, orient="records", force_ascii=False)

def load_predictions():
    if not os.path.exists(PREDICT_FILE):
        return pd.DataFrame()
    return pd.read_json(PREDICT_FILE)

# ===============================
# 📊 NBA驗證
# ===============================
def check_results():

    preds = load_predictions()
    if preds.empty:
        send("❌ 沒預測紀錄")
        return

    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={ODDS_API_KEY}&daysFrom=1"
    res = requests.get(url)

    if res.status_code != 200:
        return

    data = res.json()

    win, lose = 0, 0
    msg = "📊【NBA預測結果】\n━━━━━━━━━━\n\n"

    for _, p in preds.iterrows():
        for g in data:

            home = g["home_team"]
            away = g["away_team"]

            match = f"{nba_zh.get(away,away)} vs {nba_zh.get(home,home)}"

            if match == p["match"]:

                try:
                    hs = int(g["scores"][0]["score"])
                    as_ = int(g["scores"][1]["score"])
                except:
                    continue

                winner = home if hs > as_ else away
                winner_zh = nba_zh.get(winner,winner)

                if winner_zh == p["pick"]:
                    msg += f"✔ {match}\n"
                    win += 1
                else:
                    msg += f"❌ {match}\n"
                    lose += 1

    total = win + lose
    rate = round(win/total*100,1) if total>0 else 0

    msg += f"\n━━━━━━━━━━\n🎯 命中率 {rate}% ({win}/{total})"
    send(msg)

# ===============================
# 🚀 主程式（時間控制）
# ===============================
def main():

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    hour = now.hour

    print("目前時間:", hour)

    # 🟢 凌晨1點 → NBA
    if hour == 1:

        data = get_nba()
        df = analyze_nba(data)

        if df.empty:
            send("❌ NBA無比賽")
            return

        save_predictions(df)

        msg = "🔥【NBA今日預測】🔥\n━━━━━━━━━━\n\n"

        for _, r in df.head(8).iterrows():
            msg += f"{r['match']}\n👉 {r['bet']}：{r['pick']}\n👉 {round(r['prob']*100,1)}% {r['star']}\n\n"

        send(msg)
        return

    # 🔵 晚上6點 → MLB + NBA驗證
    if hour == 18:

        data = get_mlb()
        df = analyze_mlb(data)

        if not df.empty:
            msg = "⚾【MLB明日預測】⚾\n━━━━━━━━━━\n\n"

            for _, r in df.head(6).iterrows():
                msg += f"{r['match']}\n👉 {r['pick']} {r['star']}\n\n"

            send(msg)

        check_results()
        return

# ===============================
if __name__ == "__main__":
    main()
