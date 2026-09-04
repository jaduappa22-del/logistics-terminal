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
st.markdown('<p class="sub-title">실시간 물류 운임, 환율, 원자재 마켓 동향 및 핵심 업계 인텔리전스 터미널</p>', unsafe_allow_html=True)
st.divider()

# 화면 분할: 좌측(대시보드 및 레포트), 우측(주요 뉴스 탑 5 고정 패널)
col_left, col_right = st.columns([3, 1])

with col_right:
    st.markdown("### 🔥 실시간 주요 물류 뉴스 TOP 5")
    st.markdown('<div class="news-box">', unsafe_allow_html=True)
    
    # 주요 뉴스 링크 리스트 (실무용 주요 매체 및 공신력 있는 링크 연결)
    news_items = [
        {"title": "1. 상하이컨테이너운임지수(SCFI) 반등세 전환", "url": "https://www.shippingazette.com"},
        {"title": "2. 파나마 운하 통항량 제한 완화 조치 발표", "url": "https://www.reuters.com"},
        {"title": "3. 주요 선사들 아시아-유럽 노선 운임 인상 예고", "url": "https://gcaptain.com"},
        {"title": "4. 글로벌 항만 적체 현황 및 물류 대란 리스크 점검", "url": "https://www.lloydslist.com"},
        {"title": "5. 친환경 선박 연료 규제 강화에 따른 해운업계 영향", "url": "https://www.tradewindsnews.com"}
    ]
    
    for item in news_items:
        st.markdown(f"- [{item['title']}]({item['url'])")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📌 Quick Links")
    st.markdown("- [블룸버그 마켓](https://www.bloomberg.com)")
    st.markdown("- [야후 파이낸스](https://finance.yahoo.com)")
    st.markdown("- [해운물류정보공식포털](https://www.portmis.go.kr)")

with col_left:
    st.markdown("### 📊 핵심 물류 지표 & 매크로 터미널 (Real-time)")
    
    # 야후 파이낸스를 통한 실시간 데이터 로드 (환율, 원유, 금속 등 물류 연동 지표)
    tickers = {
        "WTI 원유 (해운 연료비 연동)": "CL=F",
        "USD/KRW (원/달러 환율)": "KRW=X",
        "Drewry 상하이-LA 운임(추정)": "BDRY", # 해운 ETF 지표 대체 예시
        "Copper (컨테이너/제조 원자재)": "HG=F"
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
    st.markdown("### 📑 주간 물류 시장 동향 및 리포트 요약")
    
    # 탭으로 상세 레포트 구성
    tab1, tab2, tab3 = st.tabs(["🚢 해운 및 운임 동향", "🛢️ 원자재 및 공급망 이슈", "💡 자재구매팀 인사이트"])
    
    with tab1:
        st.markdown("#### [Weekly Briefing] 해운 시장 및 컨테이너 운임 분석")
        st.write("• 최근 글로벌 주요 항만의 하역 효율성이 개선되고 있으나, 지정학적 리스크로 인한 우회 노선 운항이 지속되며 톤마일(Ton-mile) 수요가 증가하고 있습니다.")
        st.write("• 상세 분석 보고서 원문은 아래 링크를 참조하세요.")
        st.markdown("[🔗 해운 시장 전문 리포트 읽기 (외부 링크)](https://www.hellenicshippingnews.com)")
        
    with tab2:
        st.markdown("#### [Supply Chain] 주요 원자재 및 에너지 수급 이슈")
        st.write("• 유가 변동성에 따른 선박 연료비(Bunker Surcharge) 추이가 안정세와 변동성을 오가고 있습니다.")
        st.write("• 주요 비철금속(구리, 알루미늄 등)의 재고량 추이에 따른 제조 원가 압박 요인을 모니터링 중입니다.")
        st.markdown("[🔗 글로벌 공급망 리스크 센터 바로가기](https://www.freightwaves.com)")
        
    with tab3:
        st.markdown("#### [Action Item] 자재구매팀 시사점")
        st.write("1. 환율(USD/KRW) 변동폭 확대에 따른 수입 원가 헤징 전략 수립 필요")
        st.write("2. 해상 운임 스팟(Spot) 요율 변동에 따른 장기 계약(SC) 갱신 시기 조율")
        st.write("3. 주요 원자재 수급 차질 대비 안전재고 수준 재점검")
