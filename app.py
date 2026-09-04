import io
import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="AFK Logistics Intelligence Desk", page_icon="⚡", layout="wide"
)

# 커스텀 CSS (DHL 스타일 포인트 + 가독성 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f5; color: #18181b; }
    .main-header { background-color: #ffcc00; padding: 20px; border-radius: 6px; color: #d40511; font-weight: 900; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e4e4e7; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .sub-header { font-size: 16px; font-weight: 700; color: #d40511; margin-bottom: 10px; }
    .headline-box { background-color: #fafafa; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #d40511; border: 1px solid #e4e4e7; margin-bottom: 8px; }
    .alert-box { background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    .safe-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 상단 AFK 시그니처 배너
st.markdown("""
    <div class="main-header">
        <span>⚡ AFK LOGISTICS INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #18181b; color: #ffcc00; padding: 4px 10px; border-radius: 4px;">OPERATIONS DESK v2.0</span>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(메인 터미널 & 시뮬레이터 & 유틸리티), 우측(퀵링크 & 병목 상태)
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
  # 1. 실시간 매크로 지표 및 위험 경보
  st.markdown(
      '<div class="card"><div class="sub-header">📊 실시간 물류 마켓 지표'
      " & 리스크 알림판</div>",
      unsafe_allow_html=True,
  )

  tickers = {
      "WTI 원유 (해운 연료비)": "CL=F",
      "USD/KRW (원/달러 환율)": "KRW=X",
      "BDRY (해운 운임 ETF)": "BDRY",
      "Copper (원자재)": "HG=F",
  }

  data_list = []
  fx_current = 0.0

  for name, ticker in tickers.items():
    try:
      t = yf.Ticker(ticker)
      hist = t.history(period="5d")
      if not hist.empty:
        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100

        if "USD/KRW" in name:
          fx_current = current_price

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

    # 🚨 리스크 임계값 알림 로직 (오타 수정 완료)
    if fx_current > 0:
      if fx_current >= 1350:
        st.markdown(
            f'<div class="alert-box">🚨 [리스크 경보] 현재 원/달러 환율({fx_current:.2f}원)이 고환율 임계치(1,350원)를 상회합니다. 수입 대금 결제 타이밍을 면밀히 검토하세요!</div>',
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            f'<div class="safe-box">✨ [정상 안정] 현재 환율({fx_current:.2f}원)은 안정권 내에 있습니다.</div>',
            unsafe_allow_html=True,
        )

  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 실무 물류비 변동 시뮬레이터 & 엑셀 다운로드
  st.markdown("""
        <div class="card">
            <div class="sub-header">🧮 실무 물류비 변동 심플 시뮬레이터 & 보고서 추출</div>
            <p style="font-size: 13px; color: #52525b; margin-bottom: 15px;">
            환율 및 운임 변동에 따른 비용 증감을 확인하고, 결과를 엑셀 파일로 바로 다운로드하여 주간 보고에 활용하세요.
            </p>
    """, unsafe_allow_html=True)

  s_col1, s_col2, s_col3 = st.columns(3)
  with s_col1:
    base_budget = st.number_input(
        "기준 월 물류비 (만원)", min_value=100, max_value=1000000, value=10000
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
        f"💡 환율 {fx_inc}%·운임 {freight_inc}% 변동 시 총"
        f" **{total_added:,.1f}만원** 증감 발생"
    )

  # 📥 엑셀 다운로드 버튼 구현
  sim_result_df = pd.DataFrame([{
      "기준 월 물류비(만원)": base_budget,
      "환율 변동률(%)": fx_inc,
      "운임 변동률(%)": freight_inc,
      "예상 증감액(만원)": round(total_added, 1),
      "조정 후 총 물류비(만원)": round(final_budget, 1),
  }])


  def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="Simulation_Report")
    return output.getvalue()


  excel_data = convert_df_to_excel(sim_result_df)

  st.download_button(
      label="📥 시뮬레이션 결과 엑셀 보고서 다운로드 (.xlsx)",
      data=excel_data,
      file_name="AFK_Logistics_Simulation_Report.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
      use_container_width=True,
  )

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. 실무 용어 & 인코텀즈 가이드 탭
  st.markdown("""
        <div class="card">
            <div class="sub-header">📚 AFK 실무 물류/무역 가이드 덱</div>
    """, unsafe_allow_html=True)

  tab_g1, tab_g2, tab_g3 = st.tabs(
      ["📦 주요 인코텀즈(Incoterms)", "📐 컨테이너 규격 상식", "💡 구매팀 리드타임 팁"]
  )

  with tab_g1:
    st.markdown(
        "**FOB (Free On Board)**: 선측 인도 조건. 수출자가 선박에 화물을 실을"
        " 때까지의 비용과 위험을 부담."
    )
    st.markdown(
        "**CIF (Cost, Insurance and Freight)**: 운임·보험료 도지 인도 조건."
        " 수입항까지의 운임과 보험료를 수출자가 부담."
    )
    st.markdown(
        "**EXW (Ex Works)**: 공장 인도 조건. 구매자가 공장 출고부터 모든"
        " 비용과 위험을 부담."
    )

  with tab_g2:
    st.markdown(
        "**20ft 컨테이너 (TEU)**: 최대 적재 중량 약 21~24톤 / CBM 약 28~30"
    )
    st.markdown(
        "**40ft 컨테이너 (FEU)**: 최대 적재 중량 약 26~29톤 / CBM 약 58~68"
    )
    st.markdown("*(※ 화물의 성상 및 포장 형태에 따라 실제 적재량은 상이)*")

  with tab_g3:
    st.markdown(
        "1. **중국발 화물**: 선적 기항지 스케줄 변동이 잦으므로 마감일 기준"
        " 최소 3일 전 부킹 완료 권장"
    )
    st.markdown(
        "2. **유럽/미주 아시아발**: 희망봉 우회 노선 상시화로 기존 대비 해상"
        " 운송 리드타임 +10~14일 여유 산정 필수"
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 실시간 뉴스 헤드라인 (원문 다이렉트)
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
            <div class="headline-box">
                <b>📰 실시간 이슈 {idx}</b><br>
                👉 <a href="{article['url']}" target="_blank" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #002855;">{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("실시간 기사를 불러오는 중입니다.")

  st.markdown("</div>", unsafe_allow_html=True)
