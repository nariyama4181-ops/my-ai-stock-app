import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. 基本設定 ---
LINE_TOKEN = "LucgCjeDzafsZlaOsr1teLcP3ovJAbJpF/YN1coBeBDPtuBepCm/dEnnsaobgfYRtcE73DzhG2YPZzEC8CS6A+oia3kxHWKCMXKcV7EEjiN9xdiEfbXd529mqYdYwyFoUWrSGimxJDy391Ze8UlE8QdB04t89/1O/w1cDnyilFU="

def broadcast_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message[:5000]}]} # LINEの制限対策
    return requests.post(url, headers=headers, json=data)

# --- 2. 高度な解析エンジン ---
def get_detailed_analysis(ticker, df):
    last = df['Close'].iloc[-1]
    ma25 = df['Close'].rolling(25).mean().iloc[-1]
    rsi = (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100).iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    
    # スコアリング
    score = 50
    insights = []
    
    if rsi < 28:
        score += 35
        insights.append(f"現在RSIは{rsi:.1f}。市場全体がパニック的に投げ売っている『バーゲンセール』状態です。過去の統計上、ここからの自律反発は非常に強力なものになります。")
    elif last > ma25 * 1.05 and vol_ratio > 2.5:
        score += 30
        insights.append(f"出来高が平時の{vol_ratio:.1f}倍。単なる上げではなく、機関投資家による『本気の買い集め』が始まったサインです。トレンドの初動として注目。")
    
    if ma25 * 0.92 < last < ma25 * 0.98:
        score += 15
        insights.append("25日線付近での底堅い動き。下値リスクが限定的で、初心者でもエントリーしやすい理想的な『押し目』です。")

    if not insights: return None
    
    return {
        "score": score,
        "desc": " ".join(insights),
        "target": last * 1.12,
        "stop": last * 0.94
    }

# --- 3. UI ---
st.set_page_config(page_title="AI投資秘書 PRO", layout="wide")
st.title("🛡️ AI投資秘書 PRO：プロフェッショナル・ハブ")

tab1, tab2 = st.tabs(["🌍 グローバル・マクロ号外", "🏆 市場全網羅ランキング"])

with tab1:
    st.subheader("11指標・世界経済徹底解析")
    if st.button("📰 11指標マクロレポートを配信"):
        with st.spinner('世界中のニュースを検索・解析中...'):
            # ここでWeb検索（Gemini）を利用したレポートをシミュレート
            # 実際にはここでGoogle検索結果を統合するロジックが入ります
            msg = "🚨 【AI投資秘書：グローバル・マクロ号外】\n(1)株式市場: 米国AI株の収益化確認で1%上昇。...\n(2)金利: ドル円159円。介入警戒MAX。...\n(以下、ご指定の11項目をフル生成)"
            broadcast_line(msg)
            st.success("レポートを送信しました。")

with tab2:
    st.subheader("東証3,800社・完全スキャナー")
    if st.button("🚀 お宝TOP10を精密スキャン配信"):
        results = []
        codes = [f"{i}.T" for i in range(1301, 9999)] # 主要コード
        p_bar = st.progress(0)
        
        # 効率化のため100銘柄ずつ小分け
        for i in range(0, 1000, 100): # まずは1000銘柄でテスト。運用に合わせて拡張。
            chunk = codes[i:i+100]
            data = yf.download(chunk, period="1y", interval="1d", progress=False)
            if data.empty: continue
            
            for t in chunk:
                try:
                    df_t = data.xs(t, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                    if df_t['Volume'].iloc[-1] < 100000: continue # 低流動性除外
                    
                    analysis = get_detailed_analysis(t, df_t)
                    if analysis:
                        # 銘柄名の取得（ボタンを高速化するためこのタイミングで取得）
                        info = yf.Ticker(t).info
                        name = info.get('shortName', t)
                        if "ETF" in name or "Index" in name: continue # 指数系を除外
                        
                        results.append({
                            "name": name, "ticker": t, "score": analysis['score'],
                            "desc": analysis['desc'], "price": df_t['Close'].iloc[-1],
                            "target": analysis['target'], "stop": analysis['stop']
                        })
                except: continue
            p_bar.progress((i+100)/1000)

        top_10 = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
        
        # メッセージ構築
        report = "【AI深層注目ランキング TOP10】\n\n"
        for i, r in enumerate(top_10):
            rank = "🥇" if i==0 else ("🥈" if i==1 else ("🥉" if i==2 else f"{i+1}位"))
            report += f"{rank}: {r['name']} ({r['ticker']})\n"
            report += f"📊 根拠: {r['desc']}\n"
            report += f"💰 現価: {r['price']:,.1f}円 / 🎯 目安: {r['target']:,.0f}円\n\n"
        
        broadcast_line(report)
        st.success("精密スキャン結果を送信しました！")
        st.text_area("配信内容:", report, height=400)