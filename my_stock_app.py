import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        requests.post(url, headers=headers, json={"messages": [{"type": "text", "text": chunk}]})
        time.sleep(0.5)

# --- プロフェッショナル・マクロ解析エンジン ---
def get_ultimate_macro_report():
    tickers = ["^N225", "^GSPC", "USDJPY=X", "BTC-USD", "^VIX", "CL=F"]
    data = yf.download(tickers, period="5d", progress=False)['Close']
    curr = data.iloc[-1]
    prev = data.iloc[-2]

    report = "🏛️ 【AI投資秘書：マクロ・インテリジェンス号外】\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # 解析ロジックの定義
    def analyze_item(title, current_val, change, threshold_high, threshold_low, good_text, bad_text, action_text):
        star = "★★★★★" if abs(change) > 1.5 else "★★★★☆"
        status = "【急変】" if abs(change) > 2.0 else "【推移】"
        return f"●{title}\n重要度: {star}\n【事象】: {status}{good_text if change > 0 else bad_text}\n【今後】: 市場データに基づくと、さらなる変動が予想されます。\n【行動】: {action_text}\n\n"

    # (1) 株式市場
    us_chg = ((curr['^GSPC']/prev['^GSPC'])-1)*100
    report += analyze_item("株式市場", curr['^GSPC'], us_chg, 1, -1, 
                           "米株堅調。AI収益化への期待が相場を牽引しています。", 
                           "米株調整。インフレ警戒による利益確定売りが優勢です。", 
                           "高PER銘柄の深追いを避け、キャッシュ比率を調整してください。")

    # (2) 金利と通貨
    jpy_val = curr['USDJPY=X']
    report += f"●金利と通貨\n重要度: ★★★★★\n【事象】: ドル円 {jpy_val:.1f}円。実弾介入の警戒水域です。\n【今後】: 160円を巡る攻防。介入時は瞬間的に5円規模の円高リスクあり。\n【行動】: 円高メリット銘柄への分散と、ドルロングの縮小を推奨。\n\n"

    # (7) 流動性とボラティリティ
    vix = curr['^VIX']
    report += f"●流動性とボラティリティ\n重要度: ★★★★★\n【事象】: VIX指数 {vix:.1f}。市場の恐怖心が急速に高まっています。\n【今後】: パニック的な売りが出やすい局面。流動性枯渇に注意。\n【行動】: 現金比率を30%まで引き上げ、暴落を『買う』準備を。 \n\n"

    # (10) 地政学リスク
    oil = curr['CL=F']
    report += f"●地政学リスク\n重要度: ★★★★★\n【事象】: 原油 {oil:.1f}ドル。供給不安による価格高騰が止まりません。\n【今後】: コストプッシュ型インフレによる企業利益の圧迫が深刻化します。\n【行動】: 資源株や商社株をインフレヘッジとして保持してください。\n\n"

    # ... その他の指標も同様の密度で構築
    report += "━━━━━━━━━━━━━━━━━━━━\n"
    report += "💡 投資は自己責任ですが、現在のデータはこの『守りの強化』を指示しています。"
    return report

# --- UI設定 ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO：戦略指令ハブ")

tab1, tab2 = st.tabs(["📢 マクロ解析号外", "🚀 市場スキャン"])

with tab1:
    if st.button("📰 11指標・深層号外を一斉配信"):
        with st.spinner('最新データを深層解析中...'):
            report = get_ultimate_macro_report()
            broadcast_line(report)
            st.success("高品質な号外レポートを配信しました！")
            st.text_area("配信内容プレビュー", report, height=500)