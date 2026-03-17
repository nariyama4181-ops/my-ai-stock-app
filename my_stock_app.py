import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# --- 設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

# 楽天証券等で注目度の高い「日本株スキャン対象リスト」(約40-50銘柄)
SCAN_UNIVERSE = {
    "トヨタ": "7203.T", "三菱UFJ": "8306.T", "東京エレクトロン": "8035.T", "ソニーG": "6758.T", 
    "ソフトバンクG": "9984.T", "任天堂": "7974.T", "キーエンス": "6861.T", "ファストリ": "9983.T",
    "レーザーテック": "6920.T", "三井住友FG": "8316.T", "三菱商事": "8058.T", "武田薬品": "4502.T",
    "JT": "2914.T", "日本郵船": "9101.T", "日立": "6501.T", "リクルート": "6098.T",
    "信越化学": "4063.T", "伊藤忠": "8001.T", "三井物産": "8031.T", "KDDI": "9433.T",
    "村田製作所": "6981.T", "日本電信電話": "9432.T", "アドバンテスト": "6857.T", "ダイキン": "6367.T",
    "オリックス": "8591.T", "三菱地所": "8802.T", "ルネサス": "6723.T", "楽天G": "4755.T"
}

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

def deep_scan(name, ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # 1. 勢い（5日線/25日線乖離）
        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        ma25 = df['Close'].rolling(25).mean().iloc[-1]
        # 2. 売られすぎ（RSI）
        rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
        # 3. 直近ボラティリティ
        volatility = df['Close'].pct_change().std()
        
        # --- AIスコアリングロジック ---
        score = 50
        if ma5 > ma25: score += 15 # 上昇トレンド
        if rsi < 40: score += 20    # 割安・底値圏
        if rsi > 75: score -= 20    # 過熱気味
        if ma5 > ma25 * 1.05: score += 10 # 強いモメンタム
        
        # 理由の自動生成
        if rsi < 35: reason = "市場で売られすぎており、絶好のリバウンド局面です。"
        elif ma5 > ma25: reason = "強い上昇トレンドが発生中。波に乗るチャンスです。"
        elif score > 65: reason = "業績・チャートともに安定感があり、押し目買い推奨です。"
        else: reason = "現在は静観し、次の反発タイミングを待つのが賢明です。"
        
        return {"name": name, "score": score, "reason": reason, "price": df['Close'].iloc[-1]}
    except:
        return None

st.set_page_config(page_title="AI注目銘柄スキャナー", layout="wide")
st.title("🏛️ AI的注目ランキング TOP15：日本株深層スキャン")

if st.button("🚀 注目銘柄50社をスキャンしてTOP15を配信"):
    with st.spinner('全銘柄のチャートと需給をAIが解析中...（これには1分ほどかかります）'):
        results = []
        progress = st.progress(0)
        
        for i, (name, ticker) in enumerate(SCAN_UNIVERSE.items()):
            analysis = deep_scan(name, ticker)
            if analysis: results.append(analysis)
            progress.progress((i + 1) / len(SCAN_UNIVERSE))
        
        # スコア上位15銘柄を抽出
        top_15 = sorted(results, key=lambda x: x['score'], reverse=True)[:15]
        
        msg = "【AI的注目ランキング TOP15】\n\n"
        msg += "楽天証券等の注目銘柄から、今買うべき「期待値の高い株」を選出しました。\n\n"
        
        for i, res in enumerate(top_15):
            rank_icon = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"{i+1}位"))
            msg += f"{rank_icon}: {res['name']} ({res['score']}点)\n"
            msg += f"💰 価格: {res['price']:,.1f}円\n"
            msg += f"💡 理由: {res['reason']}\n\n"
        
        msg += "--------------------------\n"
        msg += "※スコア70点以上が『即戦力候補』、60点以上が『監視推奨』です。"
        
        resp = broadcast_line(msg)
        if resp.status_code == 200:
            st.success("最新のTOP15ランキングを一斉送信しました！")
            st.text_area("送信内容プレビュー:", msg, height=400)