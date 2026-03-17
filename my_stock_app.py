import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

def get_market_pulse():
    msg = "🚨 【AI投資秘書：マーケット号外】\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    indices = {
        "^N225": "🇯🇵 日本株 (日経平均)",
        "^GSPC": "🇺🇸 米国株 (S&P500)",
        "USDJPY=X": "💴 為替 (ドル円)",
        "BTC-JPY": "💰 仮想通貨 (BTC)"
    }
    
    for ticker, label in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            # 前日比の計算
            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            price = hist['Close'].iloc[-1]
            diff_icon = "🔥 急騰中" if change > 1.5 else ("📈 堅調" if change > 0 else ("📉 軟調" if change > -1.5 else "😱 急落中"))
            
            msg += f"■ {label}\n"
            msg += f"　価格: {price:,.1f} / 前日比: {change:+.2f}%\n"
            msg += f"　状況: {diff_icon}\n"
            
            # ニュース取得
            news = t.news[:1]
            if news:
                msg += f"　トピック: {news[0]['title'][:40]}...\n"
            else:
                # ニュースがない場合はAIが「価格変動の理由」を一般論で補足
                if change > 1.0:
                    msg += "　見解: 市場はリスクオン。買い圧力が強く、さらなる上値追いの可能性があります。\n"
                elif change < -1.0:
                    msg += "　見解: 利益確定売りが先行。サポートライン（支持線）まで引きつけるのが吉です。\n"
                else:
                    msg += "　見解: 方向感を探る展開。無理なエントリーは避け、静観を推奨します。\n"
            msg += "\n"
        except:
            continue
            
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 【投資家への提言】\n"
    msg += "現在のボラティリティに基づき、資金の3割はキャッシュで保持しつつ、強い銘柄への集中投資を検討してください。"
    return msg

# --- Streamlit 画面 ---
st.title("🛡️ AI投資秘書：号外配信ハブ")

if st.button("📰 最新マーケット号外を一斉配信"):
    with st.spinner('市場の温度感を精密測定中...'):
        report = get_market_pulse()
        resp = broadcast_line(report)
        if resp.status_code == 200:
            st.success("「中身のある」号外を配信しました！")
            st.text_area("配信内容:", report, height=400)