import yfinance as yf
import pandas as pd
import requests
import os
import time

# GitHub Secretsから取得
LINE_TOKEN = os.getenv("LINE_TOKEN")

TICKER_NAMES = {
    "1810.T": "松井建設", "8306.T": "三菱UFJ", "8035.T": "東京エレクトロン", "6758.T": "ソニーG",
    "9984.T": "SBG", "7974.T": "任天堂", "6861.T": "キーエンス", "9983.T": "ファストリ",
    "6920.T": "レーザーテック", "8316.T": "三井住友FG", "8058.T": "三菱商事", "4502.T": "武田薬品",
    "2914.T": "JT", "9101.T": "日本郵船", "6501.T": "日立", "6098.T": "リクルート",
    "4063.T": "信越化学", "8001.T": "伊藤忠", "8031.T": "三井物産", "9433.T": "KDDI",
    "9201.T": "JAL", "9202.T": "ANA", "6301.T": "コマツ", "5803.T": "フジクラ", "7203.T": "トヨタ"
}

def broadcast_line(message):
    if not message or not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    # 文字数制限対策で分割送信
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        requests.post(url, headers=headers, json={"messages": [{"type": "text", "text": chunk}]})
        time.sleep(0.5)

def generate_dynamic_insight(df):
    """テクニカル指標に基づいた深層解析文の生成"""
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    
    # RSI解析
    if rsi < 25: rsi_text = f"RSI {rsi:.1f}。パニック売りが極まった歴史的売られすぎ水準です。"
    elif rsi < 40: rsi_text = f"RSI {rsi:.1f}。過熱感は完全に消え、リバウンドのエネルギーを蓄積中。"
    else: rsi_text = f"RSI {rsi:.1f}。需給は安定しており、トレンド追随が可能な水準です。"

    # トレンド解析
    diff = ((last / ma25) - 1) * 100
    if diff > 5: trend_text = f"25日線から{diff:.1f}%上放れ。強い上昇慣性が継続しています。"
    elif diff < -5: trend_text = f"25日線から{abs(diff):.1f}%乖離。自律反発のバネが限界まで溜まっています。"
    else: trend_text = "移動平均線に収束中。ブレイクアウト直前の重要な局面です。"

    vol_text = f"出来高も平時の{vol_r:.1f}倍と活況です。" if vol_r > 1.8 else "需給は平穏です。"
    return f"{rsi_text} {trend_text} {vol_text}"

if __name__ == "__main__":
    watchlist = list(TICKER_NAMES.keys())
    data = yf.download(watchlist, period="1y", progress=False)
    
    results = []
    for t in watchlist:
        try:
            df = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
            rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
            
            # 評価ロジック：売られすぎ、または強いトレンドをスコアリング
            score = 50
            if rsi < 30: score += 30
            if df['Close'].iloc[-1] > df['Close'].rolling(25).mean().iloc[-1]: score += 20
            
            results.append({
                "name": TICKER_NAMES[t], "code": t, "score": score,
                "insight": generate_dynamic_insight(df),
                "price": df['Close'].iloc[-1]
            })
        except: continue
    
    top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
    
    msg = "🏆 【AI投資秘書：深層注目ランキング TOP 10】\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, r in enumerate(top_10):
        rank = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位", "9位", "10位"][i]
        msg += f"{rank}: {r['name']} ({r['code']})\n"
        msg += f"📊 解析: {r['insight']}\n"
        msg += f"💰 現価: {r['price']:,.1f}円 / 🎯 目安: {r['price']*1.12:,.0f}円\n\n"
    
    broadcast_line(msg)