import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# --- 1. 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

STOCKS = {
    "トヨタ": "7203.T", "任天堂": "7974.T", "ソニーG": "6758.T", "SBG": "9984.T", 
    "ファストリ": "9983.T", "キーエンス": "6861.T", "三菱UFJ": "8306.T", 
    "東エレク": "8035.T", "リクルート": "6098.T", "信越化学": "4063.T"
}
CRYPTOS = {
    "ビットコイン": "BTC-JPY", "イーサリアム": "ETH-JPY", "リップル": "XRP-JPY", 
    "ソラナ": "SOL-JPY", "ドージコイン": "DOGE-JPY"
}

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

# --- 2. 予測エンジン（1銘柄ずつリアルタイム解析） ---
def get_prediction(name, ticker_symbol):
    try:
        # 過去1年分のデータを取得
        df = yf.download(ticker_symbol, period="1y", interval="1d", progress=False)
        if df.empty: return f"・{name}: データ取得不可"
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        # 指標計算（MA, RSI）
        df['MA5'] = df['Close'].rolling(5).mean()
        df['RSI'] = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean()) * 100
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        train = df.dropna()
        features = ['Close', 'MA5', 'RSI']
        
        # AI学習
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(train[features][:-1], train['Target'][:-1])
        pred = model.predict(train[features].tail(1))[0]
        
        icon = "📈 上昇" if pred == 1 else "📉 停滞"
        return f"・{name}: {icon}"
    except:
        return f"・{name}: 解析エラー"

# --- 3. ニュース取得（簡易版：Yahooのヘッドラインを取得） ---
def fetch_real_news():
    try:
        # 代表として日経平均のニュースを取得
        n225 = yf.Ticker("^N225")
        news_list = n225.news[:3] # 最新3件
        news_text = "📰 【最新マーケットトピック】\n"
        for n in news_list:
            news_text += f"・{n['title'][:40]}...\n"
        return news_text + "--------------------------\n"
    except:
        return "📰 ニュース取得中（詳細は朝刊レポートをお待ちください）\n--------------------------\n"

# --- 4. メイン画面 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🏛️ AI投資秘書 PRO：一斉配信センター")

st.info("このボタンを押すと、友だち追加している全員に「本物の分析結果」が送信されます。")

if st.button("🚀 15銘柄を解析して一斉配信を実行"):
    with st.spinner('全銘柄のデータを1つずつダウンロードし、AIが計算しています...（約30秒）'):
        # ① ニュースセクション
        header = "【AI投資秘書：リアルタイム速報】\n\n"
        news_part = fetch_real_news()
        
        # ② 15銘柄の予測をループで実行
        prediction_text = "🚀 【15銘柄AI予測結果】\n"
        all_assets = {**STOCKS, **CRYPTOS}
        
        # 進捗バーを表示
        progress_bar = st.progress(0)
        for i, (name, ticker) in enumerate(all_assets.items()):
            res = get_prediction(name, ticker)
            prediction_text += res + "\n"
            progress_bar.progress((i + 1) / len(all_assets))
            
        footer = "\n🎯 詳細はアプリでチャートを確認してください。"
        
        # ③ 送信
        final_msg = header + news_part + prediction_text + footer
        resp = broadcast_line(final_msg)
        
        if resp.status_code == 200:
            st.success("全員に本物の予測結果を送信しました！")
            st.balloons()
            st.text_area("送信された内容:", final_msg, height=400)
        else:
            st.error(f"配信失敗: {resp.text}")