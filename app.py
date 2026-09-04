import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="DHL Logistics Operations Terminal", page_icon="📦", layout="wide"
)

# DHL 스타일 커스텀 CSS (강렬한 옐로우/오렌지 포인트, 뛰어난 가독성)
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f5; color: #18181b; }
    .main-header { background-color: #ffcc00; padding: 20px; border-radius: 6px; color: #d40511; font-weight: 900; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e4e4e7; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .sub-header { font-size: 16px; font-weight: 700; color: #d40511; margin-bottom: 10px; }
    .headline-item { background-color: #ffffff; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #d40511; border-top: 1px solid #e4e4e7; border-right: 1px solid #e4e4e7; border-bottom: 1px solid #e4e4e7; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# DHL 시그니처 상단 배너
st.markdown("""
    <div class="main-header">
        <span>📦 DHL LOGISTICS OPERATIONS TERMINAL</span>
        <span style="font-size: 14px; background-color: #18181b; color: #ffcc00; padding: 4px 10px; border-radius: 4px;">TEAM DAILY DESK</span>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(실무 지표 & 시뮬레이터 & 뉴스), 우측(빠른 유관기관 링크)
col_left, col_right = st.columns([3, 1])

with col_right:
  st.markdown(
      '<div class="card"><div class="sub-header">📌 유관기관 퀵링크</div>',
      unsafe_allow_html=True,
  )
  st.markdown("- [한국무역협회 (KITA)](https://www.kita.net)")
  st.markdown("- [해양수산부](https://www.mof.go.kr)")
  st.markdown("- [한국해양수산개발원](https://www.kmi.re.kr)")
  st.markdown("- [물류신문](https://www.klnews.co.kr)")
  st.markdown("- [한국해운신문](https://www.maritimepress.co.kr)")
  st.markdown("</div>", unsafe_allow_html=True)

  st.markdown(
      '<div class="card"><div class="sub-header">🚦 주요 항만/경로 상태</div>',
      unsafe_allow_html=True,
  )
  st.markdown("• **희망봉 우회**: ⚠️ 지연 지속 (+10일)")
  st.markdown("• **중국 닝보/상하이**: ⚠️ 선적 물량 집중")
  st.markdown("• **부산항 하역**: 🟢 원활 및 정상")
  st.markdown("</div>", unsafe_allow_html=True)

with col_left:
  # 1. 실시간 매크로 지표
  st.markdown(
      '<div class="card"><div class="sub-header">📊 실시간 물류 마켓 지표'
      " (Real-time)</div>",
      unsafe_allow_html=True,
  )

  tickers = {
      "WTI 원유 (해운 연료비)": "CL=F",
      "USD/KRW (원/달러 환율)": "KRW=X",
      "BDRY (해운 운임 ETF)": "BDRY",
      "Copper (원자재)": "HG=F",
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
            "지표 항목": name,
            "현재 시세": round(current_price, 2),
            "전일 대비 (%)": round(change, 2),
        })
    except:
      pass

  if data_list:
    df_indicators = pd.DataFrame(data_list)
    st.dataframe(df_indicators, use_container_width=True, hide_index=True)
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 물류팀 실무형 비용 변동 시뮬레이터 (수식 직관성 개선)
  st.markdown("""
        <div class="card">
            <div class="sub-header">🧮 실무 물류비 변동 심플 시뮬레이터</div>
            <p style="font-size: 13px; color: #52525b; margin-bottom: 15px;">
            환율과 해상 운임이 변동할 때, 우리 팀의 월간 물류비(예: 1억원 기준)가 실제로 얼마나 증감하는지 직관적으로 계산합니다.
            </p>
    """, unsafe_allow_html=True)

  s_col1, s_col2, s_col3 = st.columns(3)
  with s_col1:
    base_budget = st.number_input(
        "기준 월 물류비 (만원)", min_value=100, max_value=100000, value=10000
    )
  with s_col2:
    fx_inc = st.slider(
        "환율 상승 폭 (%)", min_value=-10.0, max_value=20.0, value=3.0, step=0.5
    )
  with s_col3:
    freight_inc = st.slider(
        "운임 상승 폭 (%)",
        min_value=-20.0,
        max_value=50.0,
        value=3.0,
        step=0.5,
    )

  # 정확하고 직관적인 계산식 (환율 영향 70%, 운임 영향 30% 반영)
  added_cost_fx = base_budget * (fx_inc / 100.0) * 0.7
  added_cost_freight = base_budget * (freight_inc / 100.0) * 0.3
  total_added = added_cost_fx + added_cost_freight
  final_budget = base_budget + total_added

  m_col1, m_col2 = st.columns(2)
  with m_col1:
    st.metric(
        label="조정 후 예상 총 물류비",
        value=f"{final_budget:,.1f} 만원",
        delta=f"{total_added:+,.1f} 만원",
    )
  with m_col2:
    st.info(
        f"💡 **분석 요약**: 환율 {fx_inc}% 및 운임 {freight_inc}% 변동 시, 총"
        f" **{total_added:,.1f}만원**의 비용 증감이 발생합니다."
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. 실시간 뉴스 헤드라인 (원문 다이렉트)
  st.markdown("""
        <div class="card">
            <div class="sub-header">🚨 실시간 물류·해운 이슈 헤드라인 (원문 연결)</div>
    """, unsafe_allow_html=True)


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
      for entry in feed.entries[:5]:
        articles.append({"title": entry.title, "url": entry.link})
      return articles
    except:
      return []


  live_news = get_logistics_news()

  if live_news:
    for idx, article in enumerate(live_news, 1):
      st.markdown(
          f"""
            <div class="headline-box" style="background-color: #fafafa; padding: 10px; border-radius: 6px; border-left: 3px solid #d40511; margin-bottom: 8px;">
                <b>📰 실시간 이슈 {idx}</b><br>
                👉 <a href="{article['url']}" target="_blank" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #002855;">{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("실시간 기사를 불러오는 중입니다.")

  st.markdown("</div>", unsafe_allow_html=True)
