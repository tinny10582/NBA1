



import requests
import pandas as pd

ODDS_API_KEY = "459db2b0ceca5d2103a479358f6b163b"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1492283303217070080/lbrvzppTz-h9EcshXSHue6NOtAJY31CjT1jWPmS0U_2MV8Ps1O1zp--rPuoGF9LlNNGk"

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

def get_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&markets=spreads,totals"
    return requests.get(url).json()

def analyze(data):

    res = []

    for g in data:

        home = g["home_team"]
        away = g["away_team"]

        spread = None
        total = None

        for b in g["bookmakers"]:
            for m in b["markets"]:

                if m["key"] == "spreads":
                    for o in m["outcomes"]:
                        if o["name"] == home:
                            spread = o["point"]

                if m["key"] == "totals":
                    total = m["outcomes"][0]["point"]

        if spread is None:
            continue

        # 🔥 台彩模擬
        spread_tw = spread - 1.5
        total_tw = total + 2

        # 🔥 套利
        diff = spread_tw - spread

        if diff <= -2:
            pick = away
            prob = 0.65
        else:
            pick = home if spread < 0 else away
            prob = 0.55

        # 🔥 大小分（動態）
        if total_tw >= 230:
            ou = "小分"
        elif total_tw <= 210:
            ou = "大分"
        else:
            ou = "小分"

        res.append({
            "match": f"{team_zh.get(away,away)} vs {team_zh.get(home,home)}",
            "pick": team_zh.get(pick,pick),
            "ou": ou,
            "prob": prob
        })

    return pd.DataFrame(res)

def main():

    data = get_games()
    df = analyze(data).sort_values(by="prob", ascending=False)

    msg = "🔥NBA推薦\n\n"

    for _, r in df.iterrows():
        msg += f"{r['match']}\n👉 {r['pick']} {r['ou']}\n\n"

    msg += "🔥串2\n"
    for _, r in df.head(2).iterrows():
        msg += f"{r['pick']} + "

    send(msg)

main()
