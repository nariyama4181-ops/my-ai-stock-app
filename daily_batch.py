import yfinance as yf
import pandas as pd
import requests
import os
import time
import random

# --- 1. 基本設定（GitHub Secretsから取得） ---
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
        print("Error: LINE_TOKEN is missing or message is empty.")
        return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        res = requests.post(url, headers=headers, json={"messages": [{"type": "text", "text": chunk}]})
        print(f"Status: {res.status_code}, Response: {res.text}")
        time.sleep(0.5)

# --- 2. 【最高品質・非定型解析エンジン】 ---
def generate_dynamic_insight(df):
    """テクニカル指標を組み合わせて、血の通った解析文を生成する"""
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    diff = ((last / ma25) - 1) * 100

    # RSIパーツ（投資家心理の洞察）
    if rsi < 30:
        rsi_msg = random.choice([
            f"RSI {rsi:.1f}。過熱感は皆無で、長期投資家が静かに買い集める『仕込み時』のサインが出ています。",
            f"RSIは{rsi:.1f}まで沈み込み、大衆がパニックに陥る中で『賢いマネー』が流入を開始する絶好の局面です。"
        ])
    elif rsi > 70:
        rsi_msg = random.choice([
            f"RSI {rsi:.1f}。短期的な過熱が極まっており、ここからは『チキンレース』の様相。利益確定の準備を。",
            f"RSIは{rsi:.1f}。山高ければ谷深し。現在の熱狂は、一時的な調整を呼び込む前兆と言えます。"
        ])
    else:
        rsi_msg = f"RSI {rsi:.1f}で推移。過熱も沈滞もしておらず、次の材料待ちでエネルギーを溜めています。"

    # トレンドパーツ（移動平均乖離率）
    if diff > 5:
        trend_msg = random.choice([
            f"25日線から{diff:.1f}%上放れ。強い上昇慣性が働いており、トレンドフォローの好機です。",
            f"移動平均線を大きく引き離す{diff:.1f}%の急伸。市場はこの銘柄の価値を再定義し始めています。"
        ])
    elif diff < -5:
        trend_text = f"25日線から{abs(diff):.1f}%乖離。自律反発のバネが限界まで引き絞られています。"
        trend_msg = f"{trend_text} ここから先は『売り手の枯渇』を待つ時間帯に入ります。"
    else:
        trend_msg = "移動平均線に収束しており、上下どちらかに大きく抜ける直前の『嵐の前の静けさ』です。"

    # 需給パーツ（出来高）
    if vol_r > 1.5:
        vol_msg = f"出来高は平時の{vol_r:.1f}倍と急増。機関投資家の本気買いが入り、局面が動いています。"
    else:
        vol_msg = "取引量は平穏。個人投資家主体の需給となっており、底堅さがあります。"

    return f"{rsi_msg} {trend_msg} {vol_msg}"

# --- 3. メイン実行ロジック ---
def run_daily_scan():
    watchlist = list(TICKER_NAMES.keys())
    # 最新データの取得
    data = yf.download(watchlist, period="1y", progress=False)
    
    results = []
    for t in watchlist:
        try:
            df = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
            rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
            
            # スコアリング（割安、または強い上昇トレンドを抽出）
            score = 50
            if rsi < 35: score += 30  # 売られすぎ
            if df['Close'].iloc[-1] > df['Close'].rolling(25).mean().iloc[-1]: score += 20 # 順張り
            
            results.append({
                "name": TICKER_NAMES[t], 
                "code": t, 
                "score": score, 
                "insight": generate_dynamic_insight(TICKER_NAMES[t], df), 
                "price": df['Close'].iloc[-1]
            })
        except Exception as e:
            print(f"Error scanning {t}: {e}")
            continue
    
    # スコア上位10銘柄を抽出
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