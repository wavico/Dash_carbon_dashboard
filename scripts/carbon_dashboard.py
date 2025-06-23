import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json 

# 페이지 설정
st.set_page_config(
    page_title="탄소배출량 및 배출권 현황",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #2E4057;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .chart-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 타이틀
st.markdown('<h1 class="main-header">🌍 탄소배출량 및 배출권 현황</h1>', unsafe_allow_html=True)

# 샘플 데이터 생성 함수
@st.cache_data
def generate_sample_data():
    # 시간 범위 설정
    years = list(range(2020, 2025))
    months = list(range(1, 13))
    
    # 1. 맵차트용 지역 데이터 (시간별)
    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    coords = {
        '서울': (37.5665, 126.9780), '부산': (35.1796, 129.0756), '대구': (35.8714, 128.6014),
        '인천': (37.4563, 126.7052), '광주': (35.1595, 126.8526), '대전': (36.3504, 127.3845),
        '울산': (35.5384, 129.3114), '세종': (36.4800, 127.2890), '경기': (37.4138, 127.5183),
        '강원': (37.8228, 128.1555), '충북': (36.8, 127.7), '충남': (36.5184, 126.8000),
        '전북': (35.7175, 127.153), '전남': (34.8679, 126.991), '경북': (36.4919, 128.8889),
        '경남': (35.4606, 128.2132), '제주': (33.4996, 126.5312)
    }
    
    regions_data = []
    for year in years:
        for month in months:
            for region in regions:
                base_co2 = np.random.uniform(410, 430)
                seasonal_effect = np.sin((month-1)/12*2*np.pi) * 5
                yearly_trend = (year - 2020) * 2
                
                regions_data.append({
                    '지역명': region,
                    '평균_이산화탄소_농도': base_co2 + seasonal_effect + yearly_trend + np.random.uniform(-3, 3),
                    '연도': year,
                    '월': month,
                    '연월': f"{year}-{month:02d}",
                    'lat': coords[region][0],
                    'lon': coords[region][1]
                })
    
    # 2. 연도별 배출량 데이터
    emissions_data = []
    for year in years:
        emissions_data.append({
            '연도': year,
            '총배출량': 650000 + (year-2020)*15000 + np.random.randint(-10000, 10000),
            '특정산업배출량': 200000 + (year-2020)*8000 + np.random.randint(-5000, 5000)
        })
    
    # 3. 시가/거래량 데이터 (연월별)
    market_data = []
    for year in years:
        for month in months:
            market_data.append({
                '연도': year,
                '월': month,
                '연월': f"{year}-{month:02d}",
                '시가': 10000 + np.random.randint(-2000, 3000) + (year-2020)*500,
                '거래량': 5000 + np.random.randint(-1000, 2000) + month*100
            })
    
    # 4. 트리맵용 업체 데이터 (연도별)
    companies = ['포스코홀딩스', '현대제철', 'SK이노베이션', 'LG화학', '삼성전자', 'SK하이닉스', '한화솔루션', 'GS칼텍스', 'S-Oil', '롯데케미칼']
    industries = ['철강', '철강', '석유화학', '화학', '전자', '반도체', '화학', '정유', '정유', '화학']
    
    treemap_data = []
    for year in years:
        for i, company in enumerate(companies):
            treemap_data.append({
                '연도': year,
                '업체명': company,
                '업종': industries[i],
                '대상년도별할당량': np.random.randint(50000, 200000) + (year-2020)*5000
            })
    
    # 5. 시계열 데이터 (지역별 CO2 농도)
    time_series_data = []
    for year in years:
        for month in months:
            for region in ['서울', '부산', '대구', '인천', '광주']:
                base_co2 = np.random.uniform(410, 425)
                seasonal_effect = np.sin((month-1)/12*2*np.pi) * 3
                yearly_trend = (year - 2020) * 1.5
                
                time_series_data.append({
                    '지역명': region,
                    '연도': year,
                    '월': month,
                    '연월': f"{year}-{month:02d}",
                    '평균_이산화탄소_농도': base_co2 + seasonal_effect + yearly_trend + np.random.uniform(-2, 2)
                })
    
    # 6. 게이지 차트용 데이터
    gauge_data = []
    for year in years:
        for month in months:
            gauge_data.append({
                '연도': year,
                '월': month,
                '연월': f"{year}-{month:02d}",
                '탄소배출권_보유수량': np.random.randint(800000, 1200000) + (year-2020)*50000,
                '현재_탄소배출량': np.random.randint(600000, 900000) + (year-2020)*30000
            })
    
    return (
        pd.DataFrame(regions_data),
        pd.DataFrame(emissions_data),
        pd.DataFrame(market_data),
        pd.DataFrame(treemap_data),
        pd.DataFrame(time_series_data),
        pd.DataFrame(gauge_data)
    )

# 데이터 로드
regions_df, emissions_df, market_df, treemap_df, timeseries_df, gauge_df = generate_sample_data()

# 메인 레이아웃: 좌측과 우측으로 분할
left_col, right_col = st.columns([1, 1.2])

# 좌측: 필터 + 게이지 + 맵 차트
with left_col:
    # 필터 섹션
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.subheader("🔍 필터 설정")

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.slider(
            "연도 선택",
            min_value=int(regions_df['연도'].min()),
            max_value=int(regions_df['연도'].max()),
            value=int(regions_df['연도'].max()),
            step=1
        )

    with col2:
        selected_month = st.slider(
            "월 선택",
            min_value=1,
            max_value=12,
            value=1,
            step=1
        )

    st.markdown('</div>', unsafe_allow_html=True)
    
    # 선택된 연도/월에 따른 데이터 필터링
    selected_date = f"{selected_year}-{selected_month:02d}"
    
    # 게이지 차트 섹션
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 현황 지표")
    
    # 게이지 데이터 필터링
    gauge_filtered = gauge_df[(gauge_df['연도'] == selected_year) & (gauge_df['월'] == selected_month)]
    
    if not gauge_filtered.empty:
        emission_allowance = gauge_filtered.iloc[0]['탄소배출권_보유수량']
        current_emission = gauge_filtered.iloc[0]['현재_탄소배출량']
        
        # 게이지 차트 생성 (수정된 버전)
        fig_gauges = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=('탄소배출권 보유수량', '현재 탄소배출량'),
            horizontal_spacing=0.2
        )

        # 탄소배출권 보유수량 게이지
        fig_gauges.add_trace(
            go.Indicator(
                mode="gauge+number",  # 'title' 제거
                value=emission_allowance,
                title={'text': f"보유수량<br><span style='font-size:0.8em;color:gray'>{selected_year}년 {selected_month}월</span>"},
                number={'suffix': " tCO₂eq", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [None, 1500000], 'tickfont': {'size': 10}},
                    'bar': {'color': "lightgreen", 'thickness': 0.8},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 500000], 'color': "lightgray"},
                        {'range': [500000, 1000000], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1200000
                    }
                }
            ),
            row=1, col=1
        )

        # 현재 탄소배출량 게이지
        fig_gauges.add_trace(
            go.Indicator(
                mode="gauge+number",  # 'title' 제거
                value=current_emission,
                title={'text': f"현재배출량<br><span style='font-size:0.8em;color:gray'>{selected_year}년 {selected_month}월</span>"},
                number={'suffix': " tCO₂eq", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [None, 1200000], 'tickfont': {'size': 10}},
                    'bar': {'color': "orange", 'thickness': 0.8},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 400000], 'color': "lightgray"},
                        {'range': [400000, 800000], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1000000
                    }
                }
            ),
            row=1, col=2
        )

        fig_gauges.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=80, b=20),
            font=dict(size=12),
            showlegend=False
        )
        st.plotly_chart(fig_gauges, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 맵 차트 섹션
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🗺️ 지역별 이산화탄소 농도 현황")
    
    # 맵 데이터 필터링
    map_filtered = regions_df[(regions_df['연도'] == selected_year) & (regions_df['월'] == selected_month)]
    
    if not map_filtered.empty:
        fig_map = go.Figure()
        
        fig_map.add_trace(go.Scattermapbox(
            lat=map_filtered["lat"],
            lon=map_filtered["lon"],
            mode='markers',
            marker=dict(
                size=map_filtered["평균_이산화탄소_농도"] / 15,
                color=map_filtered["평균_이산화탄소_농도"],
                colorscale="Reds",
                showscale=True,
                colorbar=dict(title="CO₂ 농도 (ppm)")
            ),
            text=map_filtered["지역명"],
            hovertemplate="<b>%{text}</b><br>CO₂ 농도: %{marker.color:.1f} ppm<extra></extra>",
            name="지역별 CO₂ 농도"
        ))
        
        fig_map.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=36.5, lon=127.5),
                zoom=6
            ),
            height=500,
            margin=dict(l=0, r=0, t=30, b=0),
            title=f"{selected_year}년 {selected_month}월 지역별 평균 이산화탄소 농도 분포"
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 우측: 4단계 구성 (필터 적용)
with right_col:
    # 우측 최상단: 막대 그래프 (연도별 배출량) - 선택된 연도까지만 표시
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 연도별 탄소 배출량 현황")
    
    emissions_filtered = emissions_df[emissions_df['연도'] <= selected_year]
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        x=emissions_filtered['연도'],
        y=emissions_filtered['총배출량'],
        name='총배출량',
        marker_color='gold'
    ))
    
    fig_bar.add_trace(go.Bar(
        x=emissions_filtered['연도'],
        y=emissions_filtered['특정산업배출량'],
        name='특정산업배출량',
        marker_color='steelblue'
    ))
    
    fig_bar.update_layout(
        title=f"{selected_year}년까지 연도별 배출량 비교",
        xaxis_title="연도",
        yaxis_title="배출량 (tCO₂eq)",
        barmode='group',
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 우측 중간 1: 콤보 그래프 (시가 + 거래량) - 선택된 연도의 월별 데이터
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("💹 KAU24 시가/거래량")
    
    market_filtered = market_df[market_df['연도'] == selected_year]
    
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_combo.add_trace(
        go.Bar(x=market_filtered['월'], y=market_filtered['거래량'], name="거래량", marker_color='steelblue'),
        secondary_y=False,
    )
    
    fig_combo.add_trace(
        go.Scatter(x=market_filtered['월'], y=market_filtered['시가'], mode='lines+markers', 
                  name="시가", line=dict(color='gold', width=3)),
        secondary_y=True,
    )
    
    fig_combo.update_xaxes(title_text="월")
    fig_combo.update_yaxes(title_text="거래량", secondary_y=False)
    fig_combo.update_yaxes(title_text="시가 (원)", secondary_y=True)
    fig_combo.update_layout(title=f"{selected_year}년 월별 시가/거래량 추이", height=300)
    
    st.plotly_chart(fig_combo, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 우측 중간 2: 트리맵 - 선택된 연도 데이터
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🏭 업체별 할당량 현황")
    
    treemap_filtered = treemap_df[treemap_df['연도'] == selected_year]
    
    fig_treemap = px.treemap(
        treemap_filtered,
        path=['업종', '업체명'],
        values='대상년도별할당량',
        title=f"{selected_year}년 업종별/업체별 할당량 분포",
        height=300,
        color='대상년도별할당량',
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 우측 하단: 시계열 그래프 - 선택된 연도까지의 데이터
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📈 지역별 이산화탄소 농도 시계열")
    
    timeseries_filtered = timeseries_df[timeseries_df['연도'] <= selected_year]
    
    fig_timeseries = px.line(
        timeseries_filtered,
        x='연월',
        y='평균_이산화탄소_농도',
        color='지역명',
        title=f"{selected_year}년까지 월별 지역별 CO₂ 농도 변화",
        height=300,
        markers=True
    )
    
    fig_timeseries.update_layout(
        xaxis_title="연월",
        yaxis_title="CO₂ 농도 (ppm)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_timeseries, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 사이드바에 데이터 업로드 기능 추가
with st.sidebar:
    st.header("📊 데이터 관리")
    
    st.subheader("📁 데이터 업로드")
    uploaded_files = {}
    
    uploaded_files['regions'] = st.file_uploader(
        "지역 데이터 (지역명, 평균_이산화탄소_농도, 연도, 월, lat, lon)",
        type="csv",
        key="regions"
    )
    
    uploaded_files['emissions'] = st.file_uploader(
        "배출량 데이터 (연도, 총배출량, 특정산업배출량)",
        type="csv",
        key="emissions"
    )
    
    uploaded_files['market'] = st.file_uploader(
        "시장 데이터 (연도, 월, 시가, 거래량)",
        type="csv",
        key="market"
    )
    
    uploaded_files['treemap'] = st.file_uploader(
        "업체 데이터 (연도, 업체명, 업종, 대상년도별할당량)",
        type="csv",
        key="treemap"
    )
    
    uploaded_files['gauge'] = st.file_uploader(
        "게이지 데이터 (연도, 월, 탄소배출권_보유수량, 현재_탄소배출량)",
        type="csv",
        key="gauge"
    )
    
    if st.button("🔄 데이터 새로고침"):
        st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; margin-top: 50px;'>
        <p>🌍 탄소배출량 및 배출권 현황 대시보드 | Built with Streamlit & Plotly</p>
    </div>
    """, 
    unsafe_allow_html=True
)
