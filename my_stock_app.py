import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- 1. 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

# --- 2. リアルタイムニュース号外エンジン ---
def get_timely_news():
    news_msg = "🚨 【AI投資秘書：マーケット速報】\n\n"
    # 主要指数のシンボル（日経225, S&P500, ドル円, BTC）
    indices = {
        "^N225": "🇯🇵 日本市場",
        "^GSPC": "🇺🇸 米国市場",
        "USDJPY=X": "💴 為替(ドル円)",
        "BTC-JPY": "💰 仮想通貨"
    }
    
    for ticker, label in indices.items():
        try:
            target = yf.Ticker(ticker)
            # 最新のニュース2件を取得
            latest_news = target.news[:2]
            news_msg += f"■ {label}\n"
            if latest_news:
                for n in latest_news:
                    title = n['title']
                    # 長すぎるタイトルをカット
                    display_title = (title[:45] + '...') if len(title) > 45 else title
                    news_msg += f" ・{display_title}\n"
            else:
                news_msg += " ・現在、新しいヘッドラインはありません。\n"
            news_msg += "\n"
        except:
            continue
            
    news_msg += "--------------------------\n"
    news_msg += "※現在の市場環境から、重要な動きをピックアップしました。投資判断の参考にしてください。"
    return news_msg

# --- 3. 全銘柄解析エンジン（前回のロジックを継承） ---
def evaluate_stock(ticker, df):
    if len(df) < 50: return None
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
    vol_shock = df['Volume'].iloc[-1] / vol_avg if vol_avg > 0 else 0
    
    score = 50
    if vol_shock > 3.0 and last > ma25: score += 45
    elif rsi < 25: score += 40
    elif ma25 * 1.02 < last < ma25 * 1.08: score += 30
    else: return None

    return {"name": ticker, "score": score, "price": last, "target": last * 1.15, "stop": last * 0.93}

# --- 4. 画面構成 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO：一斉配信ハブ")

# タブに分けて整理
tab1, tab2 = st.tabs(["📢 号外配信", "📊 市場スキャン"])

with tab1:
    st.header("📰 リアルタイム・ニュース配信")
    st.write("世界中の主要指数のヘッドラインを収集し、フォロワー全員に「マーケット号外」を送信します。")
    if st.button("📰 最新マーケットニュースを一斉配信"):
        with st.spinner('世界中のニュースを集約中...'):
            news_report = get_timely_news()
            resp = broadcast_line(news_report)
            if resp.status_code == 200:
                st.success("号外ニュースを一斉配信しました！")
                st.text_area("配信内容:", news_report, height=350)

with tab2:
    st.header("🚀 市場全網羅スキャナー")
    st.write("東証の全銘柄を解析し、今買うべき「お宝株ランキング」を送信します。")
    if st.button("🚀 日本市場の全銘柄からお宝株を発掘する"):
        with st.spinner('約3,800銘柄を深層解析中（3〜5分かかります）...'):
            # (全銘柄スキャンのロジックは前回同様に実行)
            ranges = [(1300, 2000), (2000, 4000), (4000, 7000), (7000, 9999)]
            results = []
            progress_bar = st.progress(0)
            for start, end in ranges:
                batch = [f"{i}.T" for i in range(start, end)]
                for j in range(0, len(batch), 100):
                    chunk = batch[j : j+100]
                    try:
                        data = yf.download(chunk, period="1y", interval="1d", progress=False)
                        if data.empty: continue
                        for t in chunk:
                            try:
                                df_t = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                                if df_t['Close'].isnull().all(): continue
                                analysis = evaluate_stock(t, df_t)
                                if analysis: results.append(analysis)
                            except: continue
                    except: continue
                progress_bar.progress((end - 1300) / (9999 - 1300))
            
            top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
            msg = "【AI市場全網羅：究極の厳選TOP10】\n\n"
            for i, res in enumerate(top_10):
                msg += f"{i+1}位: コード{res['name']} ({res['score']}点)\n💰 現価: {res['price']:,.1f}円 / 🎯 目標: {res['target']:,.1f}円\n\n"
            broadcast_line(msg)
            st.success("スキャン結果を送信しました！")

st.markdown("---")
st.caption("※朝 08:45 には、Geminiが検索したより詳細な分析レポートが自動送信されます。")