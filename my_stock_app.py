import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time
from sklearn.ensemble import RandomForestClassifier

# --- 1. 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

# --- 2. ニュース解析エンジン（空っぽにならない保証付き） ---
def get_market_pulse():
    msg = "🚨 【AI投資秘書：マーケット号外】\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    indices = {"^N225": "🇯🇵 日本株", "^GSPC": "🇺🇸 米国株", "USDJPY=X": "💴 ドル円", "BTC-JPY": "💰 仮想通貨"}
    
    for ticker, label in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            price = hist['Close'].iloc[-1]
            change = ((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            icon = "🔥急騰" if change > 1.5 else ("📈堅調" if change > 0 else ("📉軟調" if change > -1.5 else "😱急落"))
            
            msg += f"■ {label} | {icon}\n"
            msg += f"　価格: {price:,.1f} ({change:+.2f}%)\n"
            
            # 見解の自動生成（ニュースがなくても価格から判断）
            if change > 1.2: insight = "強気の買い圧力が継続。一段高の期待大。"
            elif change < -1.2: insight = "パニック売りを伴う下落。底打ちを確認するまで待機。"
            else: insight = "方向感を探る展開。無理な勝負は避ける局面。"
            msg += f"　見解: {insight}\n\n"
        except: continue
            
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 【提言】短期的な波に惑わされず、このトレンドに基づいたポジション管理を。"
    return msg

# --- 3. 全銘柄解析エンジン（お宝発掘ロジック） ---
def evaluate_stock(ticker, df):
    if len(df) < 50: return None
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_shock = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    
    score = 50
    if vol_shock > 3.0 and last > ma25:
        score += 40; reason = "【出来高急増】大口の買い集めによる急騰前夜の兆候。"
    elif rsi < 25:
        score += 35; reason = "【底値圏】売られすぎの極致。リバウンド期待大。"
    elif ma25 * 1.02 < last < ma25 * 1.08:
        score += 25; reason = "【上昇継続】綺麗な押し目。トレンドフォローに最適。"
    else: return None

    return {"name": ticker, "score": score, "reason": reason, "price": last, "target": last * 1.15, "stop": last * 0.93}

# --- 4. 画面UI構成 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🏛️ AI投資秘書 PRO：究極配信ハブ")

tab1, tab2 = st.tabs(["📢 リアルタイム号外", "🚀 市場全網羅スキャン"])

with tab1:
    st.subheader("📰 マーケット・パルス配信")
    st.info("世界市場の価格変動から『今の空気感』を瞬時に解析して配信します。")
    if st.button("📰 最新号外を一斉配信"):
        with st.spinner('グローバルデータを解析中...'):
            report = get_market_pulse()
            broadcast_line(report)
            st.success("高品質な号外レポートを配信しました！")
            st.text_area("配信内容プレビュー:", report, height=350)

with tab2:
    st.subheader("🔎 全3,800社フルスキャン")
    st.warning("実行には3〜5分かかります。日本市場のすべてからTOP10を抽出します。")
    if st.button("🚀 お宝銘柄を発掘して一斉配信"):
        with st.spinner('全上場銘柄を精査中...'):
            results = []
            ranges = [(1300, 3000), (3000, 6000), (6000, 9999)]
            p_bar = st.progress(0)
            for start, end in ranges:
                batch = [f"{i}.T" for i in range(start, end)]
                for j in range(0, len(batch), 100):
                    chunk = batch[j : j+100]
                    try:
                        data = yf.download(chunk, period="1y", interval="1d", progress=False)
                        for t in chunk:
                            try:
                                df_t = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                                res = evaluate_stock(t, df_t)
                                if res: results.append(res)
                            except: continue
                    except: continue
                p_bar.progress((end - 1300) / (9999 - 1300))
            
            top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
            msg = "【AI市場全網羅：究極のTOP10】\n\n"
            for i, r in enumerate(top_10):
                msg += f"{i+1}位: {r['name']} ({r['score']}点)\n根拠: {r['reason']}\n💰 {r['price']:,.1f}円 / 🎯 目安 {r['target']:,.0f}円\n\n"
            broadcast_line(msg)
            st.success("お宝銘柄ランキングを配信しました！")