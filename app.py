from datetime import datetime
import json
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="AFK Logistics Intelligence Desk", page_icon="⚡", layout="wide"
)

# 구글 앱스 스크립트 웹앱 배포 URL 연동
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwpTn92GyJRsUffpQDkL3TUgqperPM2Dhs8vRepGXuVP8T1uB88eYy0cTeQT8CGl6wL/exec"

# 커스텀 CSS (DHL 스타일 포인트 + 다크 레이더 존 조화)
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f5; color: #18181b; }
    .main-header { background-color: #ffcc00; padding: 20px; border-radius: 6px; color: #d40511; font-weight: 900; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e4e4e7; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .radar-card { background-color: #0f172a; color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 15px; }
    .sub-header { font-size: 16px; font-weight: 700; color: #d40511; margin-bottom: 10px; }
    .radar-sub-header { font-size: 16px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; }
    .headline-box { background-color: #fafafa; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #d40511; border: 1px solid #e4e4e7; margin-bottom: 8px; }
    .alert-box { background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    .safe-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    .risk-card-red { background-color: #450a0a; border: 1px solid #991b1b; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #f8fafc; }
    .risk-card-orange { background-color: #451a03; border: 1px solid #9a3412; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화 (항만 메모 보드, 팀 퀵 메모, 글로벌 항만 지연 데이터용)
if "port_memos" not in st.session_state:
  st.session_state.port_memos = {
      "부산항": {"status": "🟢 원활", "memo": "정상 하역 작업 진행 중"},
      "인천항": {"status": "🟢 원활", "memo": "특이사항 없음"},
      "상하이항": {"status": "⚠️ 혼잡", "memo": "성수기 물동량 집중으로 야드 적체"},
      "닝보항": {"status": "⚠️ 지연", "memo": "기상 악화로 터미널 일시 정체"},
  }

if "team_quick_memos" not in st.session_state:
  st.session_state.team_quick_memos = [
      "📌 [공지] 오후 2시 물류팀 주간 화물 스케줄 점검 회의",
      "📌 [전달] 상하이항 선적 건 관련 서류 마감 시간 확인 요망",
  ]

if "global_port_status" not in st.session_state:
  st.session_state.global_port_status = {
      "상하이항 (중국)": {
          "lat": 31.2304,
          "lon": 121.4737,
          "status": "심각 지연",
          "delay_days": "+7 ~ 10일",
          "reason": "성수기 물동량 폭증 및 야드 적체율 90% 초과",
          "risk_level": "red",
      },
      "닝보-주산항 (중국)": {
          "lat": 29.8683,
          "lon": 121.5440,
          "status": "지연 주의",
          "delay_days": "+3 ~ 5일",
          "reason": "국지적 기상 악화(풍랑 경보)로 인한 선적 일시 중단",
          "risk_level": "orange",
      },
      "부산항 (한국)": {
          "lat": 35.1796,
          "lon": 129.0756,
          "status": "정상 운영",
          "delay_days": "지연 없음",
          "reason": "부두 하역 및 야드 회전율 원활",
          "risk_level": "green",
      },
      "로스앤젤레스항 (미주)": {
          "lat": 33.7420,
          "lon": -118.2437,
          "status": "정상 운영",
          "delay_days": "지연 없음",
          "reason": "터미널 철도 연계 원활, 대기 시간 단축",
          "risk_level": "green",
      },
      "로테르담항 (유럽)": {
          "lat": 51.9244,
          "lon": 4.4777,
          "status": "혼잡",
          "delay_days": "+3일",
          "reason": "부두 인력 파업 여파 및 하역 장비 점검 지연",
          "risk_level": "orange",
      },
      "파나마 운하 통항": {
          "lat": 9.1000,
          "lon": -79.7000,
          "status": "통항 제한",
          "delay_days": "+14일 우회",
          "reason": "가뭄으로 인한 흘수 제한 및 일일 통항 척수 감축",
          "risk_level": "red",
      },
  }

# 상단 AFK 시그니처 배너
st.markdown("""
    <div class="main-header">
        <span>⚡ AFK LOGISTICS INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #18181b; color: #ffcc00; padding: 4px 10px; border-radius: 4px;">OPERATIONS DESK v4.3</span>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(메인 터미널 및 하단 레이더), 우측(퀵링크, 선사 트래킹, 항만 메모, 팀 퀵 메모)
col_left, col_right = st.columns([3, 1])

with col_right:
  # 1. 글로벌 선사 트래킹 링크 덱
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

  # 3. 항만 특이사항 실시간 메모 보드
  st.markdown(
      '<div class="card"><div class="sub-header">📋 당일 항만 실시간 메모보드</div>',
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
  for port, info in st.session_state.port_memos.items():
    st.markdown(
        f"• **{port}**: {info['status']} <br><span"
        f" style='font-size:12px; color:#52525b;'>({info['memo']})</span>",
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 물류팀 전용 사내 퀵 메모장
  st.markdown(
      '<div class="card"><div class="sub-header">📝 물류팀 퀵 메모장</div>',
      unsafe_allow_html=True,
  )
  new_team_memo = st.text_input("공유할 특이사항 입력", placeholder="예: 연차 사유 등")
  if st.button("메모 추가", use_container_width=True):
    if new_team_memo:
      st.session_state.team_quick_memos.append(new_team_memo)
      st.success("메모가 추가되었습니다!")

  if st.button("메모 전체 초기화", use_container_width=True):
    st.session_state.team_quick_memos = []
    st.success("메모가 초기화되었습니다.")

  st.markdown("---")
  for m in st.session_state.team_quick_memos:
    st.markdown(
        f"<div style='background-color: #fafafa; padding: 6px 8px;"
        f" border-radius: 4px; font-size: 13px; margin-bottom: 4px; border-left:"
        f" 3px solid #ffcc00;'>{m}</div>",
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
      "BDRY (BDI 해운운임 ETF)": "BDRY",
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

  # 2. 구글 스프레드시트(GAS) 연동 실시간 뉴스레터 브리프
  st.markdown("""
        <div class="card">
            <div class="sub-header">🚨 해운·물류 동향 실시간 브리프 (스프레드시트 연동)</div>
    """, unsafe_allow_html=True)


  @st.cache_data(ttl=300)
  def get_sheets_logistics_news():
    try:
      response = requests.get(GAS_WEB_APP_URL, timeout=10)
      if response.status_code == 200:
        return response.json()
      else:
        return []
    except:
      return []


  live_news = get_sheets_logistics_news()

  if live_news:
    for idx, article in enumerate(live_news, 1):
      keyword_label = article.get("keyword", "물류 동향")
      title_label = article.get("title", "제목 없음")
      url_label = article.get("url", "#")
      date_label = article.get("date", "")

      st.markdown(
          f"""
            <div class="headline-box">
                <b>📰 키워드: {keyword_label}</b><br>
                👉 <a href="{url_label}" target="_blank" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #002855;">{title_label}</a>
                <span style="font-size: 11px; color: #71717a; float: right;">({date_label})</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info(
        "스프레드시트로부터 최신 뉴스를 불러오지 못했거나 수집된 기사가"
        " 없습니다."
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. 글로벌 선박 위치 트랙킹 레이더 위젯
  st.markdown("""
        <div class="card">
            <div class="sub-header">🛰️ 글로벌 선박 및 컨테이너 트랙킹 퀵 레이더</div>
            <p style="font-size: 13px; color: #52525b; margin-bottom: 15px;">
            BL 번호나 컨테이너 번호 또는 선박명을 입력하여 주요 해운사 시스템에서 실시간 위치를 즉시 조회하세요.
            </p>
    """, unsafe_allow_html=True)

  track_col1, track_col2 = st.columns([2, 1])
  with track_col1:
    tracking_number = st.text_input(
        "BL 번호 또는 컨테이너 번호 입력", placeholder="예: HMMQ12345678"
    )
  with track_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Maersk 통합 조회", use_container_width=True):
      if tracking_number:
        safe_num = urllib.parse.quote(tracking_number)
        st.markdown(
            f'<meta http-equiv="refresh" content="0;url=https://www.maersk.com/tracking/{safe_num}">',
            unsafe_allow_html=True,
        )
        st.success(f"'{tracking_number}' 트랙킹 페이지로 연동 중입니다.")
      else:
        st.warning("번호를 입력해 주세요.")

  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 컨테이너 CBM 및 체적 간이 계산기
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

  total_cbm = (box_l * box_w * box_h / 1000000.0) * box_qty
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

  # 5. 실무 용어 & 인코텀즈 완벽 가이드 덱
  st.markdown("""
        <div class="card">
            <div class="sub-header">📚 AFK 실무 물류/무역 가이드 덱</div>
    """, unsafe_allow_html=True)

  tab_g1, tab_g2, tab_g3 = st.tabs(
      [
          "📦 인코텀즈(Incoterms) 비용/위험 가이드",
          "📐 컨테이너 규격 상식",
          "💡 구매팀 리드타임 팁",
      ]
  )

  with tab_g1:
    st.markdown(
        "#### 🚢 인코텀즈 조건별 비용 및 위험 이전 타이밍 비교"
    )
    incoterms_data = [
        {
            "구분": "EXW (공장 인도)",
            "위험 이전": "공장 출고 직후",
            "비용 부담": "공장 출고 전까지",
            "특징": "수출자 최소 의무 / 수입자 모든 책임",
        },
        {
            "구분": "FCA (운송인 인도)",
            "위험 이전": "지정 장소 인도 시",
            "비용 부담": "지정 장소까지",
            "특징": "국내 지정 터미널/창고 인도",
        },
        {
            "구분": "FOB (본선 인도)",
            "위험 이전": "선박 적재(On Board) 순간",
            "비용 부담": "선적항 본선 적재까지",
            "특징": "가장 대중적인 해상 운송 조건",
        },
        {
            "구분": "CFR (운임 포함 인도)",
            "위험 이전": "선박 적재 시 (FOB 동일)",
            "비용 부담": "수입항 운임 포함",
            "특징": "위험은 국내, 운임은 수입항까지 수출자 부담",
        },
        {
            "구분": "CIF (운임·보험료 포함)",
            "위험 이전": "선박 적재 시 (FOB 동일)",
            "비용 부담": "수입항 운임 + 보험료 포함",
            "특징": "CFR에 해상 보험 조건 추가",
        },
        {
            "구분": "DAP (목적지 도착 인도)",
            "위험 이전": "수입국 목적지 도착 시",
            "비용 부담": "목적지 하차 전까지",
            "특징": "수입국 현장까지 운송 및 리스크 수출자 부담",
        },
        {
            "구분": "DDP (관세지급 인도)",
            "위험 이전": "수입국 목적지 하차 시",
            "비용 부담": "수입 관세 및 통관 포함",
            "특징": "수출자가 관세까지 완납 (수입자 문 앞 배달)",
        },
    ]
    st.dataframe(
        pd.DataFrame(incoterms_data),
        use_container_width=True,
        hide_index=True,
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

  # 6. 글로벌 공급망 지연 & 지오 리스크 레이더 콘솔
  st.markdown("""
        <div class="radar-card">
            <div class="radar-sub-header">🚨 AFK GLOBAL SUPPLY CHAIN DELAY & RISK RADAR</div>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 15px;">
            전 세계 주요 항만 및 거점별 실시간 지연 상황을 수동으로 업데이트하여 팀원들과 공유하세요.
            </p>
    """, unsafe_allow_html=True)

  with st.expander(
      "⚙️ [관리자용] 거점별 지연 상황 및 사유 수동 업데이트 툴"
  ):
    edit_port = st.selectbox(
        "수정할 거점 선택",
        list(st.session_state.global_port_status.keys()),
        key="edit_p",
    )
    current_info = st.session_state.global_port_status[edit_port]

    new_stat = st.selectbox(
        "상태 변경",
        ["정상 운영", "지연 주의", "심각 지연", "혼잡", "통항 제한"],
        index=[
            "정상 운영",
            "지연 주의",
            "심각 지연",
            "혼잡",
            "통항 제한",
        ].index(current_info["status"]),
        key="edit_s",
    )
    new_delay = st.text_input(
        "지연 일수 변경", value=current_info["delay_days"], key="edit_d"
    )
    new_reason = st.text_input(
        "지연 사유 변경", value=current_info["reason"], key="edit_r"
    )
    new_level = st.selectbox(
        "리스크 심각도 (색상)",
        ["green", "orange", "red"],
        index=["green", "orange", "red"].index(current_info["risk_level"]),
        key="edit_l",
    )

    if st.button("거점 정보 즉시 반영", use_container_width=True):
      st.session_state.global_port_status[edit_port] = {
          "lat": current_info["lat"],
          "lon": current_info["lon"],
          "status": new_stat,
          "delay_days": new_delay,
          "reason": new_reason,
          "risk_level": new_level,
      }
      st.success(f"'{edit_port}' 현황이 실시간으로 갱신되었습니다!")

  current_data_list = []
  for p_name, p_val in st.session_state.global_port_status.items():
    current_data_list.append({
        "port": p_name,
        "lat": p_val["lat"],
        "lon": p_val["lon"],
        "status": p_val["status"],
        "delay_days": p_val["delay_days"],
        "reason": p_val["reason"],
        "risk_level": p_val["risk_level"],
    })

  port_risk_df = pd.DataFrame(current_data_list)

  r_col1, r_col2 = st.columns([2, 1])

  with r_col1:
    st.markdown(
        '<p style="font-size: 14px; font-weight: 600; color: #38bdf8;">🗺️ 전 세계'
        " 주요 거점 리스크 레이더 맵</p>",
        unsafe_allow_html=True,
    )
    st.map(port_risk_df, latitude="lat", longitude="lon", size=60, zoom=1)

  with r_col2:
    st.markdown(
        '<p style="font-size: 14px; font-weight: 600; color: #f87171;">⚡ 긴급 지연'
        " 거점 요약</p>",
        unsafe_allow_html=True,
    )
    for _, row in port_risk_df.iterrows():
      if row["risk_level"] == "red":
        st.markdown(
            f"""
                <div class="risk-card-red">
                    <b>🔴 {row['port']} ({row['status']})</b><br>
                    <span style="font-size: 12px; color: #fca5a5;">지연: <b>{row['delay_days']}</b></span><br>
                    <span style="font-size: 11px; color: #cbd5e1;">원인: {row['reason']}</span>
                </div>
            """,
            unsafe_allow_html=True,
        )
      elif row["risk_level"] == "orange":
        st.markdown(
            f"""
                <div class="risk-card-orange">
                    <b>🟠 {row['port']} ({row['status']})</b><br>
                    <span style="font-size: 12px; color: #fdba74;">지연: <b>{row['delay_days']}</b></span><br>
                    <span style="font-size: 11px; color: #cbd5e1;">원인: {row['reason']}</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

  st.markdown(
      '<p style="font-size: 14px; font-weight: 600; color: #38bdf8; margin-top:'
      ' 15px;">📋 거점별 상세 지연 인텔리전스</p>',
      unsafe_allow_html=True,
  )
  st.dataframe(
      port_risk_df[["port", "status", "delay_days", "reason"]],
      use_container_width=True,
      hide_index=True,
  )

  st.markdown("</div>", unsafe_allow_html=True)
