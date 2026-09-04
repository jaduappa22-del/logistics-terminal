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

# 세션 상태 초기화 (항만 메모 보드용)
if "port_memos" not in st.session_state:
  st.session_state.port_memos = {
      "부산항": {"status": "🟢 원활", "memo": "정상 하역 작업 진행 중"},
      "인천항": {"status": "🟢 원활", "memo": "특이사항 없음"},
      "상하이항": {"status": "⚠️ 혼잡", "memo": "성수기 물동량 집중으로 야드 적체"},
      "닝보항": {"status": "⚠️ 지연", "memo": "기상 악화로 터미널 일시 정체"},
  }

# 상단 AFK 시그니처 배너
st.markdown("""
    <div class="main-header">
        <span>⚡ AFK LOGISTICS INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #18181b; color: #ffcc00; padding: 4px 10px; border-radius: 4px;">OPERATIONS DESK v3.0</span>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(메인 터미널, 시뮬레이터, CBM 계산기, 가이드, 뉴스), 우측(퀵링크, 선사 트래킹 덱, 항만 메모보드)
col_left, col_right = st.columns([3, 1])

with col_right:
  # 1. 글로벌 선사 트래킹 링크 덱 (추가 기능 1)
  st.markdown(
      '<div class="card"><div class="sub-header">🌐 글로벌 주요 선사 트래킹</div>',
      unsafe_allow_html=True,
  )
  st.markdown("- [Maersk Tracking](https://www.maersk.com/tracking)")
  st.markdown("- [MSC Cargo Tracking](https://www.msc.com/en/track-a-shipment)")
  st.markdown("- [HMM (현대상선)](https://www.hmm21.com)")
  st.markdown(
      "- [CMA CGM Tracking](https://www.cma-cgm.com/ebusiness/tracking)"
  )
  st.markdown("- [Evergreen Line](https://www.evergreen-line.com)")
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 유관기관 퀵링크
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

  # 3. 항만 특이사항 실시간 메모 보드 (추가 기능 3)
  st.markdown(
      '<div class="card"><div class="sub-header">📋 당일 항만 실시간 메모보드</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 12px; color: #71717a;">팀원 누구나 현장 특이사항을'
      " 업데이트할 수 있습니다.</p>",
      unsafe_allow_html=True,
  )

  selected_port = st.selectbox(
      "대상 항만 선택", list(st.session_state.port_memos.keys())
  )
  new_status = st.selectbox(
      "상태", ["🟢 원활", "⚠️ 혼잡", "⚠️ 지연", "❌ 마비/중단"]
  )
  new_memo = st.text_input("특이사항 메모 입력", value="")

  if st.button("항만 현황 업데이트", use_container_width=True):
    st.session_state.port_memos[selected_port] = {
        "status": new_status,
        "memo": new_memo if new_memo else "특이사항 없음",
    }
    st.success(f"{selected_port} 현황이 갱신되었습니다!")

  st.markdown("---")
  # 현재 등록된 항만 상태 요약 표시
  for port, info in st.session_state.port_memos.items():
    st.markdown(
        f"• **{port}**: {info['status']} <br><span"
        f" style='font-size:12px; color:#52525b;'>({info['memo']})</span>",
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

with col_left:
  # 1. 실시간 매크로 지표 및 위험 경보
  st.markdown(
      '<div class="card"><div class="sub-header">📊 실시간 물류 마켓 지표'
      " & 리스크 알림판</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 13px; color: #52525b; margin-bottom: 12px;">💡'
      " <b>환율 리스크 기준 안내</b>: 수입 원가 손익분기 및 최근 환율"
      " 변동성을 고려하여 <b>1,350원</b>을 적정 기준선(Threshold)으로"
      " 관리합니다.</p>",
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

    if fx_current > 0:
      if fx_current >= 1350:
        st.markdown(
            f'<div class="alert-box">🚨 [환율 경보] 현재 원/달러 환율({fx_current:.2f}원)이 적정 기준선(1,350원)을 초과했습니다. 수입 대금 결제 시 주의가 필요합니다.</div>',
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            f'<div class="safe-box">✨ [환율 안정] 현재 원/달러 환율({fx_current:.2f}원)은 적정 기준선(1,350원) 미만으로 안정권입니다.</div>',
            unsafe_allow_html=True,
        )

  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 실무 물류비 변동 심플 시뮬레이터
  st.markdown("""
        <div class="card">
            <div class="sub-header">🧮 실무 물류비 변동 심플 시뮬레이터</div>
            <p style="font-size: 13px; color: #52525b; margin-bottom: 15px;">
            환율과 해상 운임 변동에 따른 비용 증감을 직관적으로 계산합니다.
            </p>
    """, unsafe_allow_html=True)

  s_col1, s_col2, s_col3 = st.columns(3)
  with s_col1:
    base_budget = st.number_input(
        "기준 월 물류비 (만원)", min_value=100, max_value=1000000, value=10000
    )
  with s_col2:
    fx_inc = st.slider(
        "환율 상승 폭 (%)", min_value=-10.0, max_value=20.0, value=0.0, step=0.5
    )
  with s_col3:
    freight_inc = st.slider(
        "운임 상승 폭 (%)",
        min_value=-20.0,
        max_value=50.0,
        value=3.0,
        step=0.5,
    )

  added_cost_fx = base_budget * (fx_inc / 100.0) * 0.5
  added_cost_freight = base_budget * (freight_inc / 100.0) * 0.5
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
        f"💡 환율 {fx_inc}%·운임 {freight_inc}% 변동 시, 당사 포트폴리오 기준"
        f" 총 **{total_added:,.1f}만원**의 증감이 발생합니다."
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. 컨테이너 CBM 및 체적 간이 계산기 (추가 기능 2)
  st.markdown("""
        <div class="card">
            <div class="sub-header">📦 컨테이너 CBM 및 적재율 간이 계산기</div>
            <p style="font-size: 13px; color: #52525b; margin-bottom: 15px;">
            화물 박스의 규격과 수량을 입력하여 총 CBM을 산출하고, 20ft/40ft 컨테이너 적재 참고 비율을 확인하세요.
            </p>
    """, unsafe_allow_html=True)

  c_col1, c_col2, c_col3, c_col4 = st.columns(4)
  with c_col1:
    box_l = st.number_input("가로 (cm)", min_value=1.0, value=50.0)
  with c_col2:
    box_w = st.number_input("세로 (cm)", min_value=1.0, value=40.0)
  with c_col3:
    box_h = st.number_input("높이 (cm)", min_value=1.0, value=30.0)
  with c_col4:
    box_qty = st.number_input("총 박스 수량", min_value=1, value=500)

  # CBM 계산: (가로 x 세로 x 높이 / 1,000,000) * 수량
  total_cbm = (box_l * box_w * box_h / 1000000.0) * box_qty
  # 20ft 기준 적재 한계 약 28 CBM, 40ft 기준 약 58 CBM 가정
  fill_20ft = (total_cbm / 28.0) * 100
  fill_40ft = (total_cbm / 58.0) * 100

  res_c1, res_c2, res_c3 = st.columns(3)
  with res_c1:
    st.metric(label="총 화물 체적 (CBM)", value=f"{total_cbm:,.2f} CBM")
  with res_c2:
    st.metric(
        label="20ft 컨테이너 기준 적재율", value=f"{fill_20ft:,.1f}%"
    )
  with res_c3:
    st.metric(
        label="40ft 컨테이너 기준 적재율", value=f"{fill_40ft:,.1f}%"
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 실무 용어 & 인코텀즈 가이드 탭
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

  # 5. 실시간 뉴스 헤드라인 (원문 다이렉트)
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
