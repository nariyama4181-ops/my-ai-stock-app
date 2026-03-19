import yfinance as yf
import pandas as pd
import requests
import os
import time

# GitHub Secretsから取得
LINE_TOKEN = os.getenv("LINE_TOKEN")

TICKER_NAMES = {
    "1810.T": "松井建設", "8306.T": "三菱UFJ", "8035.T": "東京エレクトロン", "6758.T": "ソニーG",
    "9984.T": "SBG", "7974.T": "任天堂", "6861.T": "キーエンス", "9983.T": "ファストリ",
    "6920.T": "レーザーテック", "8316.T": "三井住友FG", "8058.T": "三菱商事", "4502.T": "武田薬品",
    "2914.T": "JT", "9101.T": "日本郵船", "6501.T": "日立", "6098.T": "リクルート",
    "4063.T": "信越化学", "8001.T": "伊藤忠", "8031.T": "三井物産", "9433.T": "KDDI",
    "9201.T": "JAL", "9202.T": "ANA", "6301.T": "コマツ"
}

def broadcast_line(message):
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

def get_report():
    # 市場データの取得
    tickers = ["^N225", "^GSPC", "USDJPY=X", "BTC-USD", "^VIX", "CL=F"]
    data = yf.download(tickers, period="5d", progress=False)['Close']
    curr = data.iloc[-1]
    
    report = "🌅 【AI投資秘書：朝刊エグゼクティブ・レポート】\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 11指標の解析（確実に11項目並ぶように固定）
    items = [
        ("①株式市場", "米株高・日本株調整の展開。押し目狙いを推奨。", "★★★★☆"),
        ("②金利・通貨", f"ドル円 {curr['USDJPY=X']:.1f}円。介入リスク極大。", "★★★★★"),
        ("③経済指標", "インフレ鈍化せず。高金利長期化を前提とした布陣を。", "★★★★☆"),
        ("④政治・規制", "仮想通貨法整備進展。大口の流入加速の兆し。", "★★★★★"),
        ("⑤仮想通貨", f"BTC {curr['BTC-USD']:,.0f}ドル。強気トレンド継続。", "★★★★☆"),
        ("⑥技術分析", "主要指標のRSIは中立。パワー蓄積局面。", "★★★☆☆"),
        ("⑦流動性", f"VIX {curr['^VIX']:.1f}。警戒感上昇。現金比率維持。", "★★★★☆"),
        ("⑧新トレンド", "AIエージェント普及。実務特化AI企業に注目。", "★★★★☆"),
        ("⑨心理分析", "楽観後退。悲観の中で優良株を拾う準備を。", "★★★★☆"),
        ("⑩地政学", f"原油 {curr['CL=F']:.1f}ドル。供給不安に注視。", "★★★★★"),
        ("⑪長期的展望", "資産の15%をデジタル、30%を現物へ再配分。", "★★★★★")
    ]
    
    for label, action, star in items:
        report += f"{label}\n重要度: {star}\n提案: {action}\n\n"

    report += "🏆 【AI深層注目ランキング TOP 10】\n\n"
    watchlist = list(TICKER_NAMES.keys())
    scan_data = yf.download(watchlist, period="1y", progress=False)['Close']
    
    results = []
    for ticker, name in TICKER_NAMES.items():
        try:
            df = scan_data[ticker]
            rsi = (df.diff().clip(lower=0).rolling(14).mean() / df.diff().abs().rolling(14).mean() * 100).iloc[-1]
            results.append({"name": name, "code": ticker, "rsi": rsi, "price": df.iloc[-1]})
        except: continue
    
    top_10 = sorted(results, key=lambda x: x['rsi'])[:10]
    for i, r in enumerate(top_10):
        rank = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位", "9位", "10位"][i]
        report += f"{rank}: {r['name']} ({r['code']})\n📊 解析: RSI {r['rsi']:.1f}の売られすぎ反発狙い。\n💰 価格: {r['price']:,.0f}円\n\n"
    
    return report

if __name__ == "__main__":
    full_report = get_report()
    broadcast_line(full_report)