import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(
    page_title="Global Logistics & Supply Chain Terminal",
    page_icon="🚢",
    layout="wide",
)

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 700; color: #1e293b; }
    .sub-title { font-size: 14px; color: #64748b; margin-bottom: 20px; }
    .headline-box { background-color: #ffffff; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="main-title">🚢 Global Supply Chain & Logistics'
    " Intelligence</p>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">실시간 물류 운임, 환율, 원자재 마켓 동향 및 실시간'
    " 뉴스 원문 터미널</p>",
    unsafe_allow_html=True,
)
st.divider()

col_left, col_right = st.columns([3, 1])

with col_right:
  st.markdown("### 📌 공신력 있는 유관기관")
  st.markdown("- [한국무역협회 (KITA)](https://www.kita.net)")
  st.markdown("- [해양수산부](https://www.mof.go.kr)")
  st.markdown("- [한국해양수산개발원](https://www.kmi.re.kr)")
  st.markdown("- [물류신문](https://www.klnews.co.kr)")
  st.markdown("- [한국해운신문](https://www.maritimepress.co.kr)")

  st.markdown("---")
  st.markdown("### 🔗 Quick Links")
  st.markdown("- [관세무역데이터](https://www.customs.go.kr)")
  st.markdown("- [포트미스 항만물류](https://www.portmis.go.kr)")

with col_left:
  st.markdown("### 📊 핵심 물류 지표 & 매크로 터미널 (Real-time)")

  tickers = {
      "WTI 원유 (해운 연료비 연동)": "CL=F",
      "USD/KRW (원/달러 환율)": "KRW=X",
      "BDRY (글로벌 해운 운임 ETF)": "BDRY",
      "Copper (제조 및 물류 원자재)": "HG=F",
  }

  data_list = []
  for name, ticker in tickers.items():
    try:
      t = yf.Ticker(ticker)
      hist = t.history(period="5d")
      if not hist.empty:
        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        data_list.append({
            "지표명": name,
            "현재가": round(current_price, 2),
            "전일 대비 변동률 (%)": round(change, 2),
        })
    except:
      pass

  if data_list:
    df_indicators = pd.DataFrame(data_list)
    st.dataframe(df_indicators, use_container_width=True, hide_index=True)

  st.markdown("---")

  st.markdown(
      "### 🚨 실시간 물류 이슈 & 해운동향 핵심 기사 (구글 뉴스 실시간 연동)"
  )
  st.markdown(
      "접속 시점에 수집된 최신 물류/해운 관련 주요 기사 원문 링크입니다."
  )


  # 구글 뉴스 RSS 안전하게 가져오기 (URL 인코딩 적용)
  @st.cache_data(ttl=600)
  def get_logistics_news():
    try:
      raw_query = "해운 운임 선박 항만 물류"
      encoded_query = urllib.parse.quote(raw_query)
      rss_url = (
          f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
      )

      feed = feedparser.parse(rss_url)
      articles = []

      for entry in feed.entries[:6]:
        articles.append({"title": entry.title, "url": entry.link})
      return articles
    except Exception as e:
      return []


  live_news = get_logistics_news()

  if live_news:
    for idx, article in enumerate(live_news, 1):
      st.markdown(
          f"""
            <div class="headline-box">
                <b>📰 실시간 이슈 {idx}</b><br>
                👉 <a href="{article['url']}" target="_blank" style="text-decoration: none; font-size: 15px; font-weight: 600; color: #2563eb;">{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("현재 실시간 기사를 불러오는 중입니다. 잠시 후 새로고침해 주세요.")

  st.markdown("---")
  st.markdown("### 📑 주간 물류 시장 동향 및 자재구매팀 인사이트")

  tab1, tab2, tab3 = st.tabs(
      ["🚢 해운 및 운임 동향", "🛢️ 원자재 및 공급망 이슈", "💡 자재구매팀 Action Item"]
  )

  with tab1:
    st.markdown("#### [Market Trend] 해운 및 운임 동향 요약")
    st.write(
        "• 지정학적 리스크와 우회 노선 항해가 고착화되면서 톤마일 증가 및 운임"
        " 변동성이 상시화되었습니다."
    )
    st.write(
        "• 중국 항만 적체 및 기상 악화 변수가 발생할 경우 스케줄 지연 리스크가"
        " 커지므로 상단 실시간 기사를 수시로 확인하시기 바랍니다."
    )

  with tab2:
    st.markdown("#### [Supply Chain] 공급망 및 리스크 요인")
    st.write(
        "• 환율 및 해상 운임 스팟 요율의 등락이 자재 수입 원가에 미치는 영향을"
        " 주 단위로 점검하고 있습니다."
    )

  with tab3:
    st.markdown("#### [Action Item] 구매팀 대응 전략")
    st.write(
        "1. 항만 적체 및 선박 지연에 대비해 핵심 품목의 리드타임(Lead Time)을"
        " 평소보다 1~2주 여유 있게 산정"
    )
    st.write(
        "2. 주요 운임 지수 및 환율 변동 추이에 따른 장기 계약 및 스팟 계약 비중"
        " 탄력적 조절"
    )
