import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# --- 設定：お送りいただいた最新情報をセット ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "Uce6411ae299c82e7c03aa3b0c771def9"

# --- 銘柄マスター（最高に選びやすいリスト） ---
STOCKS = {
    "トヨタ自動車": "7203.T", "任天堂": "7974.T", "ソニーグループ": "6758.T",
    "ソフトバンクG": "9984.T", "ファーストリテイリング": "9983.T", "キーエンス": "6861.T",
    "三菱UFJ FG": "8306.T", "東京エレクトロン": "8035.T", "リクルートHD": "6098.T", "信越化学": "4063.T"
}
CRYPTOS = {
    "ビットコイン (BTC)": "BTC-JPY", "イーサリアム (ETH)": "ETH-JPY",
    "リップル (XRP)": "XRP-JPY", "ソラナ (SOL)": "SOL-JPY", "ドージコイン (DOGE)": "DOGE-JPY"
}

# --- LINE送信関数 ---
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    return requests.post(url, headers=headers, json=data)

# --- ページ設定 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🏛️ AI投資秘書：プロフェッショナル・ダッシュボード")

# --- UI：銘柄選択プルダウン（サイドバー） ---
st.sidebar.header("📊 資産ポートフォリオ")
asset_cat = st.sidebar.radio("アセットクラスを選択", ["日本株 (主要10銘柄)", "暗号資産 (主要5銘柄)"])

if asset_cat == "日本株 (主要10銘柄)":
    selected_name = st.sidebar.selectbox("銘柄を選択してください", list(STOCKS.keys()))
    ticker_symbol = STOCKS[selected_name]
else:
    selected_name = st.sidebar.selectbox("通貨を選択してください", list(CRYPTOS.keys()))
    ticker_symbol = CRYPTOS[selected_name]

# --- 運用・リスク設定 ---
st.sidebar.markdown("---")
budget = st.sidebar.number_input("投資総予算 (円)", value=1000000, step=100000)
loss_cut_rate = st.sidebar.slider("損切りライン (%)", 1, 20, 5)

# --- データ取得 & エラーガード ---
@st.cache_data(ttl=3600)
def load_data(symbol):
    if not symbol: return pd.DataFrame() # 空の場合は空のDFを返す
    data = yf.download(symbol, period="3y", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = load_data(ticker_symbol)

if df.empty:
    st.error("データの取得に失敗しました。銘柄コードを確認してください。")
    st.stop()

current_price = df['Close'].iloc[-1]

# --- メインレイアウト ---
tab1, tab2 = st.tabs(["🎯 リアルタイム戦略", "📈 パフォーマンス検証"])

with tab1:
    st.subheader(f"🔍 {selected_name} ({ticker_symbol}) の分析")
    col1, col2, col3 = st.columns(3)
    
    stop_loss_price = current_price * (1 - loss_cut_rate / 100)
    col1.metric("現在価格", f"{current_price:,.1f} 円")
    col2.metric("損切り目安", f"{stop_loss_price:,.1f} 円", delta=f"-{loss_cut_rate}%")
    
    # チャート表示
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(height=450, margin=dict(l=0, r=0, b=0, t=30))
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🚀 AIに投資戦略を指示させる"):
        with st.spinner('計算中...'):
            # AI学習ロジック（簡略化版）
            df['MA5'] = df['Close'].rolling(5).mean()
            df['RSI'] = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean()) * 100
            df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
            train = df.dropna()
            
            features = ['Close', 'MA5', 'RSI']
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(train[features][:-1], train['Target'][:-1])
            pred = model.predict(train[features].tail(1))[0]
            
            res = "【上昇傾向 📈】" if pred == 1 else "【下落注意 📉】"
            shares = (budget * 0.2) / current_price
            if asset_cat == "日本株 (主要10銘柄)": shares = (shares // 100) * 100
            
            msg = f"【AI秘書通知】\n対象: {selected_name}\n判定: {res}\n目標数量: {shares:.2f}\n損切価格: {stop_loss_price:,.1f}円"
            
            resp = send_line(msg)
            if resp.status_code == 200:
                st.success(f"予測結果: {res} をLINEに送信しました！")
                st.balloons()
            else:
                st.error(f"LINE送信失敗(Code:{resp.status_code}): {resp.text}")

with tab2:
    st.write("過去1年間のAI戦略シミュレーション（準備中）")