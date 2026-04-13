
import requests
import pandas as pd
import os
import datetime

print("🔥 系統啟動")

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492338812011942013/G9MNjKNpDJ4HlKa0CbxCeAifse1yamhpJvCn9BtZC8DZor_NEnVw0xUK1aWB9LPfNQ62"

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
        print("📤 發送:", msg[:100])
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        print("❌ Discord失敗")

# ===============================
# API
# ===============================
def get_nba():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

def get_mlb():
    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API_KEY}&markets=totals"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# ===============================
# 勝率模型
# ===============================
def winrate_spread(s):
    s = abs(s)
    if s >= 9: return 0.67
    elif s >= 7: return 0.63
    elif s >= 5: return 0.58
    else: return 0.52

def winrate_total(t):
    if t >= 235: return ("小分", 0.63)
    elif t <= 210: return ("大分", 0.62)
    else: return ("略過", 0.50)

def star(p):
    if p >= 0.65: return "⭐⭐⭐"
    elif p >= 0.60: return "⭐⭐"
    else: return "⭐"

# ===============================
# NBA分析
# ===============================
def analyze_nba(data):

    results = []

    for g in data:
        try:
            home = g["home_team"]
            away = g["away_team"]

            spread, total = None, None

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
# MLB分析
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
                "prob": prob,
                "star": star(prob)
            })

        except:
            continue

    return pd.DataFrame(results)

# ===============================
# 儲存/讀取
# ===============================
def save_predictions(df):
    df.to_json(PREDICT_FILE, orient="records", force_ascii=False)

def load_predictions():
    if not os.path.exists(PREDICT_FILE):
        return pd.DataFrame()
    return pd.read_json(PREDICT_FILE)

# ===============================
# NBA驗證
# ===============================
def check_results():

    preds = load_predictions()
    if preds.empty:
        send("❌ 沒預測紀錄")
        return

    win, lose = 0, 0

    msg = "📊【NBA命中率】\n━━━━━━━━━━\n\n"

    for _, p in preds.iterrows():
        msg += f"👉 {p['match']}\n"

    msg += "\n（驗證API可再升級）"

    send(msg)

# ===============================
# 主程式
# ===============================
def main():

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    hour = now.hour

    force_run = True  # 🔥 手動測試開關（測試完改False）

    print("目前時間:", hour)

    # =========================
    # NBA
    # =========================
    if hour == 1 or force_run:

        print("🔥 NBA執行")

        data = get_nba()
        df = analyze_nba(data)

        if df.empty:
            send("❌ NBA無比賽")
        else:
            save_predictions(df)

            msg = "🔥【NBA預測】🔥\n━━━━━━━━━━\n\n"

            for _, r in df.head(5).iterrows():
                msg += f"{r['match']}\n👉 {r['bet']}：{r['pick']} {r['star']}\n\n"

            send(msg)

    # =========================
    # MLB
    # =========================
    if hour == 18 or force_run:

        print("🔥 MLB執行")

        data = get_mlb()
        df = analyze_mlb(data)

        if not df.empty:
            msg = "⚾【MLB預測】⚾\n━━━━━━━━━━\n\n"

            for _, r in df.head(5).iterrows():
                msg += f"{r['match']}\n👉 {r['pick']} {r['star']}\n\n"

            send(msg)

        check_results()

# ===============================
if __name__ == "__main__":
    main()
