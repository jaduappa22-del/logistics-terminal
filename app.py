import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="Global Supply Chain Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
)

# 딥 네이비 & 다크 모드 기반의 하이엔드 테크니컬 UI 스타일링
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    .main-title { font-size: 26px; font-weight: 800; color: #38bdf8; letter-spacing: -0.5px; }
    .sub-title { font-size: 13px; color: #94a3b8; margin-bottom: 20px; }
    .metric-card { background-color: #1e293b; padding: 18px; border-radius: 10px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .headline-box { background-color: #1e293b; padding: 12px 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; border-left: 4px solid #38bdf8; }
    .ai-briefing { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 10px; border: 1px solid #0284c7; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# 상단 타이틀
col_t1, col_t2 = st.columns([4, 1])
with col_t1:
  st.markdown(
      '<p class="main-title">⚡ GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE</p>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p class="sub-title">Executive Decision-Making Terminal | Real-time'
      " Macro & Risk Monitor</p>",
      unsafe_allow_html=True,
  )
with col_t2:
  st.markdown(
      "<span style='background-color: #0284c7; color: white; padding: 6px"
      " 12px; border-radius: 20px; font-size: 12px; font-weight: 600;'>🟢 SYSTEM"
      " LIVE</span>",
      unsafe_allow_html=True,
  )

st.divider()

# 🧠 CPO / 임원진용 AI 모닝 브리핑 패널
st.markdown("""
    <div class="ai-briefing">
        <h4 style="color: #38bdf8; margin-top: 0; margin-bottom: 8px;">🤖 CPO Executive Morning Briefing (AI 분석 요약)</h4>
        <p style="color: #e2e8f0; font-size: 14px; margin-bottom: 0;">
        • <b>종합 리스크 진단</b>: 환율(USD/KRW) 변동성 확대 및 주요 항만 적체 현상 지속으로 수입 원가 및 리드타임 관리 주의 필요.<br>
        • <b>Action Item</b>: 하단 <b>물류비 시뮬레이터</b>를 활용하여 환율 및 운임 변동에 따른 비용 영향을 선제적으로 검토하시기 바랍니다.
        </p>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(핵심 지표 및 시뮬레이터, 뉴스), 우측(공신력 있는 유관기관 링크)
col_left, col_right = st.columns([3, 1])

with col_right:
  st.markdown("### 📌 공신력 유관기관")
  st.markdown("- [한국무역협회 (KITA)](https://www.kita.net)")
  st.markdown("- [해양수산부](https://www.mof.go.kr)")
  st.markdown("- [한국해양수산개발원](https://www.kmi.re.kr)")
  st.markdown("- [물류신문](https://www.klnews.co.kr)")
  st.markdown("- [한국해운신문](https://www.maritimepress.co.kr)")

  st.markdown("---")
  st.markdown("### 🔗 Quick Links")
  st.markdown("- [관세무역데이터](https://www.customs.go.kr)")
  st.markdown("- [포트미스 항만물류](https://www.portmis.go.kr)")

  st.markdown("---")
  st.markdown("### 🚦 주요 병목 현황")
  st.markdown("• **수에즈/희망봉**: ⚠️ 우회 운항 지속")
  st.markdown("• **중국 닝보/상하이**: ⚠️ 성수기 적체 경보")
  st.markdown("• **파나마 운하**: 🟢 통항 제한 완화")

with col_left:
  st.markdown("### 📊 실시간 매크로 & 물류 지표 터미널")

  tickers = {
      "WTI 원유 (연료비)": "CL=F",
      "USD/KRW (환율)": "KRW=X",
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
            "Market Indicator": name,
            "Current Price": round(current_price, 2),
            "Change (%)": round(change, 2),
        })
    except:
      pass

  if data_list:
    df_indicators = pd.DataFrame(data_list)
    st.dataframe(df_indicators, use_container_width=True, hide_index=True)

  st.markdown("---")

  # 🧮 임원 보고용 하이라이트 기능: 수입 원가 & 물류비 What-if 시뮬레이터
  st.markdown(
      "### 🧮 수입 원가 및 물류비 변동 시뮬레이터 (What-if Analysis)"
  )
  st.markdown(
      "환율 및 해상 운임 변동 폭에 따른 당사 수입 총비용 증감액을 실시간으로"
      " 시뮬레이션합니다."
  )

  with st.container():
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
      base_cost = st.number_input(
          "월 기본 수입/물류 예산 (억원)", min_value=1.0, max_value=100.0, value=10.0
      )
    with col_s2:
      fx_change = st.slider(
          "환율 변동률 (%)", min_value=-10.0, max_value=20.0, value=0.0, step=0.5
      )
    with col_s3:
      freight_change = st.slider(
          "해상 운임 변동률 (%)",
          min_value=-20.0,
          max_value=50.0,
          value=0.0,
          step=1.0,
      )

    # 시뮬레이션 계산
    calculated_cost = base_cost * (
        1 + (fx_change * 0.7) + (freight_change * 0.3)
    )  # 환율 가중치 70%, 운임 가중치 30% 가정
    diff_cost = calculated_cost - base_cost

    st.metric(
        label="시뮬레이션 적용 후 예상 월 총비용",
        value=f"{calculated_cost:.2f} 억원",
        delta=(
            f"+{diff_cost:.2f} 억원 (비용 증가)"
            if diff_cost > 0
            else (
                f"{diff_cost:.2f} 억원 (비용 절감)"
                if diff_cost < 0
                else "변동 없음"
            )
        ),
    )

  st.markdown("---")

  # 🚨 실시간 뉴스 기사 원문 연동 섹션
  st.markdown("### 🚨 실시간 물류 이슈 & 해운동향 핵심 기사 (원문 다이렉트)")


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
            <div class="headline-box">
                <b>🔥 실시간 헤드라인 {idx}</b><br>
                👉 <a href="{article['url']}" target="_blank" style="text-decoration: none; font-size: 15px; font-weight: 600; color: #38bdf8;">{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("실시간 뉴스를 불러오는 중입니다.")

  st.markdown("---")
  st.markdown("### 📑 주간 시장 인사이트 & 구매팀 대응 전략")

  tab1, tab2, tab3 = st.tabs(
      ["🚢 해운 및 운임 동향", "🛢️ 공급망 리스크", "💡 CPO Action Item"]
  )

  with tab1:
    st.markdown("#### [Market Trend] 해운 및 운임 동향")
    st.write(
        "• 주요 허브 항만 적체 현상 및 우회 노선 항해로 인한 톤마일 증가세 지속."
    )
  with tab2:
    st.markdown("#### [Risk Analysis] 공급망 리스크")
    st.write(
        "• 환율 및 원자재 가격 변동폭 확대에 따른 원가 방어 전략 수립 필요."
    )
  with tab3:
    st.markdown("#### [Executive Summary] 구매팀 핵심 대응 지침")
    st.write("1. 환율 상승 국면에 대비한 수입 대금 결제 슬롯 다변화 검토")
    st.write("2. 항만 적체 리스크 대비 핵심 원자재 안전재고 +1주일 추가 확보")
