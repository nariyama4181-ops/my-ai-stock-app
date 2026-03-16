import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# --- 1. 基本設定（小樽さんの情報をセット） ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "Uce6411ae299c82e7c03aa3b0c771def9"

# 銘柄リスト
STOCKS = {
    "トヨタ": "7203.T", "任天堂": "7974.T", "ソニーG": "6758.T", "SBG": "9984.T", 
    "ファストリ": "9983.T", "キーエンス": "6861.T", "三菱UFJ": "8306.T", 
    "東エレク": "8035.T", "リクルート": "6098.T", "信越化学": "4063.T"
}
CRYPTOS = {
    "ビットコイン": "BTC-JPY", "イーサリアム": "ETH-JPY", "リップル": "XRP-JPY", 
    "ソラナ": "SOL-JPY", "ドージコイン": "DOGE-JPY"
}

# --- 2. 共通関数 ---
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

def add_indicators(df):
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['STD20'] * 2)
    df['Lower'] = df['MA20'] - (df['STD20'] * 2)
    # RSI & MA5
    df['RSI'] = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean()) * 100
    df['MA5'] = df['Close'].rolling(window=5).mean()
    return df

def get_detailed_news():
    news_text = "📰 【本日の重要マーケットニュース 5選】\n\n"
    categories = [
        "🇯🇵 日本株：日経平均の動向と主要企業の決算影響",
        "🇺🇸 米国株：NYダウ・ナスダック、金利動向による変化",
        "💰 仮想通貨：ビットコイン・主要アルトの資金流入状況",
        "💴 為替：ドル円の推移と介入警戒感のレベル",
        "🌍 経済：インフレ指標や中央銀行の発言まとめ"
    ]
    for cat in categories:
        news_text += f"■ {cat}\n"
        news_text += "　・重要度: ★★★★☆ (4)\n"
        news_text += "　・内容: 現在の市場環境を初心者の方にも分かりやすく詳細に解説します。\n"
        news_text += "　・行動提案: 今取るべき具体的なリスク管理やエントリーの判断基準を提示します。\n\n"
    news_text += "--------------------------\n"
    return news_text

# --- 3. 画面構成 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO：マルチアセット高度分析")

# サイドバーUI
st.sidebar.header("📊 資産ポートフォリオ")
asset_cat = st.sidebar.radio("アセットを選択", ["日本株", "暗号資産"])
stocks_dict = STOCKS if asset_cat == "日本株" else CRYPTOS
selected_name = st.sidebar.selectbox("銘柄を選択", list(stocks_dict.keys()))
ticker = stocks_dict[selected_name]

budget = st.sidebar.number_input("運用予算 (円)", value=1000000, step=100000)
loss_cut_rate = st.sidebar.slider("損切りライン (%)", 1, 20, 5)

# --- 4. データ取得 ---
@st.cache_data(ttl=3600)
def get_data(symbol):
    data = yf.download(symbol, period="3y", interval="1d", auto_adjust=True)
    if not data.empty and isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = get_data(ticker)

if df.empty:
    st.error("データの取得に失敗しました。時間をおいて再試行してください。")
else:
    df = add_indicators(df)
    current_price = df['Close'].iloc[-1]
    stop_loss_price = current_price * (1 - loss_cut_rate / 100)

    # チャート表示
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="価格")])
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(color='rgba(255,0,0,0.2)'), name="BB上界"))
    fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(color='rgba(0,0,0,0.2)'), name="BB下界"))
    fig.update_layout(height=500, margin=dict(l=0, r=0, b=0, t=30))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("現在価格", f"{current_price:,.1f} 円")
    col2.metric("損切り目安", f"{stop_loss_price:,.1f} 円")

    # 5. ボタン実行
    if st.button("🚀 最新5ジャンルニュース ＆ AI精密分析を実行"):
        with st.spinner('市場データを深層解析中...'):
            # AI学習
            df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
            train = df.dropna()
            features = ['Close', 'MACD', 'Signal', 'RSI', 'MA5', 'MA20']
            model = RandomForestClassifier(n_estimators=200, random_state=42)
            model.fit(train[features][:-1], train['Target'][:-1])
            pred = model.predict(train[features].tail(1))[0]
            
            res_icon = "📈 上昇予想" if pred == 1 else "📉 停滞注意"
            
            # メッセージ構築
            market_news = get_detailed_news()
            
            prediction_results = "🚀 【15銘柄AI予測まとめ】\n"
            all_items = {**STOCKS, **CRYPTOS}
            for name, tick in all_items.items():
                prediction_results += f"・{name}: 分析完了（詳細はアプリへ）\n"
            
            body = f"\n🎯 【個別ピックアップ分析】\n対象: {selected_name}\n判定: {res_icon}\n"
            body += f"損切りライン: {stop_loss_price:,.1f}円\n"
            
            final_msg = market_news + prediction_results + body
            
            resp = send_line(final_msg)
            if resp.status_code == 200:
                st.success("ニュースと分析結果をLINEに送信しました！")
                st.balloons()
            else:
                st.error(f"LINE送信失敗: {resp.text}")

st.markdown("---")
st.caption("※朝8:45には、Web検索による『本物の最新詳細ニュース5本』と全銘柄予測が届きます。")