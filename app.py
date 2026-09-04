import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드로 전문가 대시보드 느낌 연출)
st.set_page_config(
    page_title="Global Logistics & Supply Chain Terminal",
    page_icon="🚢",
    layout="wide",
)

# 커스텀 CSS로 우측 뉴스 사이드바 스타일링 및 고급스러운 UI 연출
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 700; color: #1e293b; }
    .sub-title { font-size: 14px; color: #64748b; margin-bottom: 20px; }
    .news-box { background-color: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; }
    </style>
""", unsafe_allow_html=True)

# 상단 타이틀 영역
st.markdown('<p class="main-title">🚢 Global Supply Chain & Logistics Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">실시간 물류 운임, 환율, 원자재 마켓 동향 및 국내외 핵심 기관 인텔리전스 터미널</p>', unsafe_allow_html=True)
st.divider()

# 화면 분할: 좌측(대시보드 및 레포트), 우측(국내 주요 기관 뉴스 및 링크 탑 5 고정 패널)
col_left, col_right = st.columns([3, 1])

with col_right:
    st.markdown("### 🔥 국내 주요 물류·무역 소스 TOP 5")
    st.markdown('<div class="news-box">', unsafe_allow_html=True)
    
    # 국내 공신력 있는 물류/무역 기관 및 전문 매체 링크
    news_items = [
        {"title": "1. 한국무역협회 (KITA) 무역뉴스", "url": "https://www.kita.net"},
        {"title": "2. 해양수산부 보도자료 및 정책", "url": "https://www.mof.go.kr"},
        {"title": "3. 한국해양수산개발원 (KMI) 동향", "url": "https://www.kmi.re.kr"},
        {"title": "4. 물류신문 (전문 물류 뉴스)", "url": "https://www.klnews.co.kr"},
        {"title": "5. 한국해운신문 (해운항만 정보)", "url": "https://www.maritimepress.co.kr"}
    ]
    
    for item in news_items:
        st.markdown(f"- [{item['title']}]({item['url']})")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📌 Quick Links")
    st.markdown("- [관세무역데이터 (TRADES)]({https://www.customs.go.kr})")
    st.markdown("- [한국은행 경제통계시스템](https://ecos.bok.or.kr)")
    st.markdown("- [포트미스(PORT-MIS) 항만물류](https://www.portmis.go.kr)")

with col_left:
    st.markdown("### 📊 핵심 물류 지표 & 매크로 터미널 (Real-time)")
    
    # 야후 파이낸스를 통한 실시간 데이터 로드
    tickers = {
        "WTI 원유 (해운 연료비 연동)": "CL=F",
        "USD/KRW (원/달러 환율)": "KRW=X",
        "BDRY (글로벌 해운 운임 ETF)": "BDRY",
        "Copper (제조 및 물류 원자재)": "HG=F"
    }
    
    data_list = []
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                data_list.append({
                    "지표명": name,
                    "현재가": round(current_price, 2),
                    "전일 대비 변동률 (%)": round(change, 2)
                })
        except:
            pass
            
    if data_list:
        df_indicators = pd.DataFrame(data_list)
        st.dataframe(df_indicators, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 📑 주간 물류 시장 동향 및 레포트 요약")
    
    # 탭으로 상세 레포트 구성
    tab1, tab2, tab3 = st.tabs(["🚢 해운 및 운임 동향", "🛢️ 원자재 및 공급망 이슈", "💡 자재구매팀 인사이트"])
    
    with tab1:
        st.markdown("#### [Weekly Briefing] 해운 시장 및 컨테이너 운임 분석")
        st.write("• 국내외 해운 선사들의 노선 재편 및 주요 허브 항만 체선 상황을 주기적으로 모니터링해야 합니다.")
        st.write("• 상세한 국내 수출입 물류 통계는 우측의 **한국무역협회 및 해양수산부** 링크를 통해 원문을 확인하실 수 있습니다.")
        
    with tab2:
        st.markdown("#### [Supply Chain] 주요 원자재 및 수급 이슈")
        st.write("• 원/달러 환율 변동성에 따른 수입 원가 압박과 해상 운임(SCFI/BDI 등)의 연동 효과를 점검 중입니다.")
        st.write("• 글로벌 공급망 리스크 변동에 따른 안전재고 확보 전략 검토가 요구됩니다.")
        
    with tab3:
        st.markdown("#### [Action Item] 자재구매팀 시사점")
        st.write("1. 환율(USD/KRW) 변동폭 확대에 따른 수입 대금 결제 타이밍 점검")
        st.write("2. 주요 항만 물류 정체 상황에 따른 리드타임(Lead Time) 여유분 확보")
        st.write("3. 핵심 자재 품목별 단가 추이 모니터링 및 구매 계약 갱신 대응")
