import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

TICKER_NAMES = {
    "1810.T": "松井建設", "8306.T": "三菱UFJ", "8035.T": "東京エレクトロン", "6758.T": "ソニーG",
    "9984.T": "SBG", "7974.T": "任天堂", "6861.T": "キーエンス", "9983.T": "ファストリ",
    "6920.T": "レーザーテック", "8316.T": "三井住友FG", "8058.T": "三菱商事", "4502.T": "武田薬品",
    "2914.T": "JT", "9101.T": "日本郵船", "6501.T": "日立", "6098.T": "リクルート",
    "4063.T": "信越化学", "8001.T": "伊藤忠", "8031.T": "三井物産", "9433.T": "KDDI",
    "6981.T": "村田製作所", "9432.T": "NTT", "6857.T": "アドバンテスト", "6367.T": "ダイキン",
    "8591.T": "オリックス", "8802.T": "三菱地所", "6723.T": "ルネサス", "4755.T": "楽天G",
    "9201.T": "JAL", "9202.T": "ANA", "6301.T": "コマツ"
}

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        data = {"messages": [{"type": "text", "text": chunk}]}
        requests.post(url, headers=headers, json=data)
        time.sleep(0.5)

# 動的インサイト生成
def generate_dynamic_insight(df):
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    
    if rsi < 25: rsi_text = f"RSI {rsi:.1f}。パニック売りが極まり、強力な自律反発が目前のバーゲン価格です。"
    elif rsi < 40: rsi_text = f"RSI {rsi:.1f}。過熱感はなく、長期保有目的の買い集めが適した水準です。"
    else: rsi_text = f"RSI {rsi:.1f}。安定した推移で、次の材料待ちの状態です。"

    diff = ((last / ma25) - 1) * 100
    if diff > 5: trend_text = f"25日線から{diff:.1f}%上放れ。強い上昇慣性が働いています。"
    elif diff < -5: trend_text = f"25日線から{abs(diff):.1f}%乖離。自律反発のバネが溜まっています。"
    else: trend_text = "移動平均線に収束し、ブレイク直前の嵐の前の静けさです。"

    vol_text = f"出来高も平時の{vol_r:.1f}倍と活況で、大口の意思を感じます。" if vol_r > 1.8 else "需給は落ち着いています。"
    return f"{rsi_text} {trend_text} {vol_text}"

st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO")

tab1, tab2 = st.tabs(["📢 号外配信", "🚀 市場スキャン"])

with tab1:
    if st.button("📰 11指標レポートを一斉配信"):
        with st.spinner('解析中...'):
            tickers = ["^N225", "^GSPC", "USDJPY=X", "BTC-USD", "^VIX", "CL=F"]
            data = yf.download(tickers, period="5d", progress=False)['Close']
            curr = data.iloc[-1]
            report = "🚨 【AI投資秘書：マーケット号外】\n━━━━━━━━━━━━━━━━━━━━\n\n"
            items = [("株式市場", "米株堅調、日本株は利上げ警戒で選別色。"), ("金利・通貨", f"ドル円 {curr['USDJPY=X']:.1f}円。介入リスク大。"), ("経済指標", "インフレ粘着性。バリュー株優位。"), ("政治規制", "法整備進展で長期買い材料。"), ("仮想通貨", f"BTC {curr['BTC-USD']:,.0f}ドル。強気。"), ("技術分析", "RSI 50前後。過熱感なし。"), ("流動性", f"VIX {curr['^VIX']:.1f}。警戒感上昇。"), ("新技術", "AIエージェント商用化に期待。"), ("心理分析", "悲観の中で拾う準備を。"), ("地政学", f"原油 {curr['CL=F']:.1f}ドル。コスト増注視。"), ("長期展望", "デジタル資産と高配当株を推奨。")]
            for label, action in items: report += f"●{label}\n提案: {action}\n\n"
            broadcast_line(report)
            st.success("配信完了")

with tab2:
    if st.button("🚀 TOP 10ランキングを一斉配信"):
        with st.spinner('スキャン中...'):
            watchlist = list(TICKER_NAMES.keys())
            data = yf.download(watchlist, period="1y", progress=False)
            results = []
            for t in watchlist:
                try:
                    df = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
                    results.append({"name": TICKER_NAMES[t], "code": t, "rsi": rsi, "insight": generate_dynamic_insight(df), "price": df['Close'].iloc[-1]})
                except: continue
            top_10 = sorted(results, key=lambda x: x['rsi'])[:10]
            msg = "🏆 【AI深層注目ランキング TOP 10】\n\n"
            for i, r in enumerate(top_10):
                rank = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位", "9位", "10位"][i]
                msg += f"{rank}: {r['name']} ({r['code']})\n📊 解析: {r['insight']}\n💰 現価: {r['price']:,.1f}円 / 🎯 目安: {r['price']*1.12:,.0f}円\n\n"
            broadcast_line(msg)
            st.success("配信完了")