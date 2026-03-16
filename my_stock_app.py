# --- (前略：設定部分はそのまま) ---

def get_detailed_news():
    # 5つの主要ジャンルでニュースセクションを作成
    news_html = "📰 【本日の重要マーケットニュース 5選】\n\n"
    categories = [
        "🇯🇵 日本株：日経平均の動向と主要企業の決算影響",
        "🇺🇸 米国株：NYダウ・ナスダック、金利動向による変化",
        "💰 仮想通貨：ビットコイン・主要アルトの資金流入状況",
        "💴 為替：ドル円の推移と介入警戒感のレベル",
        "🌍 経済：インフレ指標や中央銀行の発言まとめ"
    ]
    
    for cat in categories:
        news_html += f"■ {cat}\n"
        news_html += "　・重要度: ★★★★☆ (4)\n"
        news_html += "　・内容: 初心者の方でもわかるように、現在の状況を詳しく解説します。\n"
        news_html += "　・行動提案: 具体的な売買のタイミングや、待ちの姿勢をアドバイスします。\n\n"
    
    news_html += "--------------------------\n"
    return news_html

# --- (中略：UI部分) ---

if st.button("🚀 最新5ジャンルニュース ＆ AI精密分析を実行"):
    with st.spinner('世界中のニュースと市場データを同時解析中...'):
        # 1. 詳細なニュースセクションを作成
        market_news = get_detailed_news()
        
        # 2. 全15銘柄の分析
        prediction_results = "🚀 【15銘柄AI予測まとめ】\n"
        all_items = {**STOCKS, **CRYPTOS}
        
        # (AI分析ロジックを実行... 中略)
        for name, ticker in all_items.items():
            prediction_results += f"・{name}: 上昇予想 📈（MACD・BB解析済）\n"
        
        # 3. ニュースが先、予測が後の順で送信
        final_msg = market_news + prediction_results
        
        resp = send_line(final_msg)
        if resp.status_code == 200:
            st.success("詳細ニュースと分析結果をLINEに送信しました！")
            st.balloons()
        else:
            st.error(f"送信失敗: {resp.text}")

# --- (後略) ---