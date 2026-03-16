import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# --- 重要：取得したIDとトークンをここに貼り付け ---
LINE_TOKEN = "ここにアクセストークンを貼り付け"
LINE_USER_ID = "ここにUから始まるユーザーIDを貼り付け"

# --- LINE送信関数 ---
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

# --- 画面構成 ---
st.set_page_config(page_title="最強AI投資秘書", layout="wide")
st.title("💼 AI投資エージェント：戦略アドバイザー版")

# サイドバー設定
st.sidebar.header("💰 運用設定")
budget = st.sidebar.number_input("投資総予算 (円)", min_value=100000, value=1000000, step=100000)
risk_per_trade = st.sidebar.slider("1銘柄への最大投入比率 (%)", 5, 50, 20)

ticker_symbol = st.sidebar.text_input("分析銘柄コード", "7203.T")

# --- データ取得とAI学習 ---
t_obj = yf.Ticker(ticker_symbol)
df = t_obj.history(period="3y")
info = t_obj.info
current_price = df['Close'].iloc[-1]

def get_ai_advice():
    # 指標作成（テクニカル）
    df['MA5'] = df['Close'].rolling(5).mean()
    df['RSI'] = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean()) * 100
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # ファンダメンタルズ（ROE/PER）
    roe = info.get('returnOnEquity', 0.1)
    per = info.get('trailingPE', 15)
    
    df['ROE'] = roe
    df['PER'] = per
    
    train_data = df.dropna()
    features = ['Close', 'MA5', 'RSI', 'ROE', 'PER']
    
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(train_data[features][:-1], train_data['Target'][:-1])
    
    # 予測実行
    pred = model.predict(train_data[features].tail(1))[0]
    return pred, roe, per

# --- メイン画面 ---
st.subheader(f"🔍 {info.get('longName')} の分析結果")

if st.button("AIに投資アドバイスを求める"):
    pred, roe, per = get_ai_advice()
    
    # 【新機能】購入株数の計算ロジック
    # 予算の20%を上限とし、現在の株価で割る（単元株100株単位を考慮）
    max_invest = budget * (risk_per_trade / 100)
    recommended_shares = (max_invest // current_price // 100) * 100
    
    if pred == 1:
        status = "【上昇 📈】"
        advice = f"現在の株価 {current_price:.1f}円に対し、予算に基づき **{int(recommended_shares)}株** の購入を検討してください。"
    else:
        status = "【下落・横ばい 📉】"
        advice = "現在は「待ち」の局面です。無理なエントリーは控えましょう。"

    # 画面表示
    st.success(f"予測結果: {status}")
    st.info(f"アドバイス: {advice}")
    
    # LINE通知
    msg = (f"【AI投資秘書】\n"
           f"銘柄: {info.get('longName')}\n"
           f"予測: {status}\n"
           f"現在値: {current_price:.1f}円\n"
           f"推奨株数: {int(recommended_shares)}株\n"
           f"ROE: {roe*100:.1f}% / PER: {per:.1f}倍")
    
    try:
        send_line(msg)
        st.balloons()
        st.write("✅ スマホのLINEにアドバイスを送信しました！")
    except:
        st.error("LINE送信に失敗しました。Uから始まるIDとトークンを再確認してください。")

st.markdown("---")
st.caption("※会計的視点: ROEが高い銘柄ほど効率的に資本を運用しています。AIもその数値を評価に加えています。")