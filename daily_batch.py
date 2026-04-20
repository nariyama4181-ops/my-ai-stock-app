import yfinance as yf
import pandas as pd
import requests
import os
import time
import random

# --- 1. 基本設定 ---
# GitHub Secretsから取得。ローカルテスト時は環境変数に設定してください。
LINE_TOKEN = os.getenv("LINE_TOKEN")

TICKER_NAMES = {
    "1810.T": "松井建設", "8306.T": "三菱UFJ", "8035.T": "東京エレクトロン", "6758.T": "ソニーG",
    "9984.T": "SBG", "7974.T": "任天堂", "6861.T": "キーエンス", "9983.T": "ファストリ",
    "6920.T": "レーザーテック", "8316.T": "三井住友FG", "8058.T": "三菱商事", "4502.T": "武田薬品",
    "2914.T": "JT", "9101.T": "日本郵船", "6501.T": "日立", "6098.T": "リクルート",
    "4063.T": "信越化学", "8001.T": "伊藤忠", "8031.T": "三井物産", "9433.T": "KDDI",
    "5803.T": "フジクラ", "7203.T": "トヨタ", "8591.T": "オリックス", "9201.T": "JAL", "9202.T": "ANA"
}

def broadcast_line(message):
    """LINEの仕様に基づき、分割して一斉送信を行う"""
    if not message or not LINE_TOKEN:
        print("❌ Error: LINE_TOKEN が設定されていません。")
        return
    
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    # LINEの1メッセージ制限に合わせて分割
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        payload = {"messages": [{"type": "text", "text": chunk}]}
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            print("✅ LINE配信成功")
        else:
            print(f"❌ LINE配信失敗: {res.status_code} - {res.text}")
        time.sleep(0.5)

# --- 2. 解析エンジン（修正済み） ---
def generate_dynamic_insight(name, df):
    """
    引数に name を追加して呼び出し側と整合性を合わせました。
    """
    try:
        last = df['Close'].iloc[-1]
        ma25 = df['Close'].rolling(25).mean().iloc[-1]
        
        # RSIの計算
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        diff = ((last / ma25) - 1) * 100

        # RSI洞察
        if rsi < 30:
            rsi_msg = f"RSI {rsi:.1f}。過熱感は皆無で、『仕込み時』のサインが出ています。"
        elif rsi > 70:
            rsi_msg = f"RSI {rsi:.1f}。短期的な過熱が極まっており、利益確定の準備を。"
        else:
            rsi_msg = f"RSI {rsi:.1f}で推移。エネルギーを溜めている段階です。"

        # トレンド洞察
        if diff > 5:
            trend_msg = f"25日線から{diff:.1f}%上放れ。強い上昇慣性が働いています。"
        elif diff < -5:
            trend_msg = f"25日線から{abs(diff):.1f}%乖離。自律反発のバネが限界です。"
        else:
            trend_msg = "移動平均線に収束しており、『嵐の前の静けさ』です。"

        return f"{rsi_msg} {trend_msg}"
    except Exception as e:
        return f"解析エラー: {e}"

# --- 3. メインロジック ---
def run_daily_scan():
    print("🔍 市場データの解析を開始します...")
    watchlist = list(TICKER_NAMES.keys())
    data = yf.download(watchlist, period="1y", progress=False)
    
    results = []
    for t in watchlist:
        try:
            # MultiIndex対応
            df = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data[t]
            
            # RSI再計算（スコアリング用）
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            score = 50
            if rsi_val < 35: score += 30
            if df['Close'].iloc[-1] > df['Close'].rolling(25).mean().iloc[-1]: score += 20
            
            results.append({
                "name": TICKER_NAMES[t], 
                "code": t, 
                "score": score, 
                "insight": generate_dynamic_insight(TICKER_NAMES[t], df), # ここを修正
                "price": df['Close'].iloc[-1]
            })
        except Exception as e:
            print(f"⚠️ {t} の解析をスキップしました: {e}")
            continue
    
    top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
    
    msg = "🏆 【AI投資秘書：深層注目ランキング TOP 10】\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, r in enumerate(top_10):
        rank = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位", "9位", "10位"][i]
        msg += f"{rank}: {r['name']} ({r['code']})\n"
        msg += f"📊 解析: {r['insight']}\n"
        msg += f"💰 現価: {r['price']:,.1f}円 / 🎯 目安: {r['price']*1.12:,.0f}円\n\n"
    
    return msg

if __name__ == "__main__":
    report = run_daily_scan()
    broadcast_line(report)