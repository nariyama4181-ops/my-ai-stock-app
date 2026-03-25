import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import random
import time

# --- 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

TICKER_NAMES = {
    "1810.T": "松井建設", "8306.T": "三菱UFJ", "8035.T": "東京エレクトロン", "6758.T": "ソニーG",
    "9984.T": "SBG", "7974.T": "任天堂", "6861.T": "キーエンス", "9983.T": "ファストリ",
    "6920.T": "レーザーテック", "8316.T": "三井住友FG", "8058.T": "三菱商事", "4502.T": "武田薬品",
    "2914.T": "JT", "9101.T": "日本郵船", "6501.T": "日立", "6098.T": "リクルート",
    "4063.T": "信越化学", "8001.T": "伊藤忠", "8031.T": "三井物産", "9433.T": "KDDI",
    "5803.T": "フジクラ", "7203.T": "トヨタ", "8591.T": "オリックス", "9201.T": "JAL", "9202.T": "ANA"
}

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        requests.post(url, headers=headers, json={"messages": [{"type": "text", "text": chunk}]})
        time.sleep(0.5)

# --- 【最高品質・非定型解析エンジン】 ---
def generate_dynamic_insight(name, df):
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    diff = ((last / ma25) - 1) * 100

    # 1. RSIパーツ（バリエーションを持たせる）
    if rsi < 30:
        rsi_msg = random.choice([
            f"RSI {rsi:.1f}。過熱感は皆無で、長期投資家が静かに買い集める『仕込み時』のサインが出ています。",
            f"RSIは{rsi:.1f}まで沈み込み、大衆がパニックに陥る中で『賢いマネー』が流入を開始する絶好の局面です。"
        ])
    elif rsi > 70:
        rsi_msg = random.choice([
            f"RSI {rsi:.1f}。短期的な過熱が極まっており、ここからは『チキンレース』の様相。利益確定の準備を。",
            f"RSIは{rsi:.1f}。山高ければ谷深し。現在の熱狂は、一時的な調整を呼び込む前兆と言えます。"
        ])
    else:
        rsi_msg = f"RSI {rsi:.1f}で推移。過熱も沈滞もしておらず、次の材料待ちでエネルギーを溜めています。"

    # 2. トレンドパーツ
    if diff > 5:
        trend_msg = random.choice([
            f"25日線から{diff:.1f}%上放れ。強い上昇慣性が働いており、トレンドフォローの好機です。",
            f"移動平均線を大きく引き離す{diff:.1f}%の急伸。市場はこの銘柄の価値を再定義し始めています。"
        ])
    elif diff < -5:
        trend_text = f"25日線から{abs(diff):.1f}%乖離。自律反発のバネが限界まで引き絞られています。"
        trend_msg = f"{trend_text} ここから先は『売り手の枯渇』を待つ時間帯に入ります。"
    else:
        trend_msg = "移動平均線に収束しており、上下どちらかに大きく抜ける直前の『嵐の前の静けさ』です。"

    # 3. 需給パーツ
    if vol_r > 1.5:
        vol_msg = f"出来高は平時の{vol_r:.1f}倍と急増。機関投資家の本気買い（または売り）が入り、局面が動いています。"
    else:
        vol_msg = "取引量は平穏。個人投資家主体の需給となっており、大崩れしにくい底堅さがあります。"

    return f"{rsi_msg} {trend_msg} {vol_msg}"

st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO：銘柄スキャナー")

if st.button("🚀 最新TOP10ランキングを一斉配信"):
    with st.spinner('全銘柄の需給データを深層解析中...'):
        watchlist = list(TICKER_NAMES.keys())
        data = yf.download(watchlist, period="1y", interval="1d", progress=False)
        results = []
        for t in watchlist:
            try:
                df = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
                # スコアリングロジック（リバウンド狙いとトレンド順張り）
                score = 50 + (30 if rsi < 30 else 0) + (20 if df['Close'].iloc[-1] > df['Close'].rolling(25).mean().iloc[-1] else 0)
                results.append({"name": TICKER_NAMES[t], "code": t, "score": score, "insight": generate_dynamic_insight(TICKER_NAMES[t], df), "price": df['Close'].iloc[-1]})
            except: continue
        
        top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
        msg = "🏆 【AI投資秘書：深層注目ランキング TOP 10】\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, r in enumerate(top_10):
            rank = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位", "9位", "10位"][i]
            msg += f"{rank}: {r['name']} ({r['code']})\n📊 解析: {r['insight']}\n💰 現価: {r['price']:,.1f}円 / 🎯 目安: {r['price']*1.12:,.0f}円\n\n"
        
        broadcast_line(msg)
        st.success("高品質なランキングをLINEに送信しました。")
        st.text_area("配信内容", msg, height=500)