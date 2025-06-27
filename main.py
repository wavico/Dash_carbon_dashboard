import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json 
import os
import base64
from PIL import Image, ImageDraw, ImageFont
import io
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="탄소배출권 통합 관리 시스템",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 40px;
    }
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #1f77b4;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .metric-highlight {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 15px 0;
    }
    .quick-stats {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .stat-item {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        margin: 0 10px;
    }
    .ranking-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .badge-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: left;
    }
    .simulator-container {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 타이틀
st.markdown('<h1 class="main-header">🌍 탄소배출권 통합 관리 시스템</h1>', unsafe_allow_html=True)

# 환영 메시지
st.markdown("""
<div class="welcome-container">
    <h2>🎯 통합 탄소배출권 관리 플랫폼</h2>
    <p><strong>탄소배출량 모니터링부터 구매 전략 수립까지, 모든 것을 한 곳에서 관리하세요.</strong></p>
    <p>이 시스템은 기업의 탄소배출권 관리를 위한 종합 솔루션을 제공합니다.<br>
    실시간 데이터 기반 분석과 AI 기반 전략 추천으로 최적의 의사결정을 지원합니다.</p>
</div>
""", unsafe_allow_html=True)

# 주요 통계 (샘플 데이터)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">📊 총 배출량</div>
                <div data-testid="metric-value">676,648 Gg CO₂eq</div>
                <div data-testid="metric-delta">2021년 기준</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">💹 KAU24 가격</div>
                <div data-testid="metric-value">8,770원</div>
                <div data-testid="metric-delta">+2.3%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">🏭 할당 대상</div>
                <div data-testid="metric-value">1,247개 업체</div>
                <div data-testid="metric-delta">3차 사전할당</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">🎯 감축 목표</div>
                <div data-testid="metric-value">40%</div>
                <div data-testid="metric-delta">2030년까지</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 주요 기능 소개
# st.markdown("## 🚀 주요 기능")

# col1, col2 = st.columns(2)

# with col1:
#     st.markdown("""
#     <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 15px 0; border-left: 5px solid #1f77b4;">
#         <h3>📊 현황 대시보드</h3>
#         <ul>
#             <li><strong>실시간 모니터링</strong>: 연도별 배출량, 지역별 CO₂ 농도</li>
#             <li><strong>시장 분석</strong>: KAU24 가격/거래량 추이</li>
#             <li><strong>할당량 현황</strong>: 업종별/업체별 분포</li>
#             <li><strong>AI 챗봇</strong>: 시나리오 시뮬레이션</li>
#         </ul>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 15px 0; border-left: 5px solid #1f77b4;">
#         <h3>🎯 구매 전략 대시보드</h3>
#         <ul>
#             <li><strong>알림 시스템</strong>: 정책/가격 급등 예고</li>
#             <li><strong>타이밍 분석</strong>: 최적 매수 시점 추천</li>
#             <li><strong>ROI 비교</strong>: 감축 vs 구매 전략 분석</li>
#             <li><strong>헤징 전략</strong>: ETF/선물 연계 포트폴리오</li>
#         </ul>
#     </div>
#     """, unsafe_allow_html=True)

# ESG 기반 탄소 감축 랭킹 시스템 구현
st.markdown('---')
st.markdown('<h2 style="text-align:center;">🏆 ESG 기반 탄소 감축 랭킹 시스템</h2>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ ESG 설정")
    
    # 기업 정보
    st.subheader("🏢 기업 정보")
    company_name = st.text_input("기업명", "삼성전자")
    industry = st.selectbox("업종", ["전자제품", "철강", "화학", "자동차", "건설", "에너지"])
    
    # 현재 ESG 점수
    current_esg_score = st.slider("현재 ESG 점수", 0, 100, 75)
    current_reduction_rate = st.slider("현재 감축률 (%)", 0, 50, 15)
    current_allocation_ratio = st.slider("할당 대비 보유율 (%)", 50, 200, 120)
    
    # 목표 설정
    st.subheader("🎯 목표 설정")
    target_esg_score = st.slider("목표 ESG 점수", 0, 100, 85)
    target_reduction_rate = st.slider("목표 감축률 (%)", 0, 50, 25)

# 1. 🥇 탄소 감축 성과 기반 ESG 랭킹 보드
st.markdown("""
<div class="ranking-card">
    <h3>🥇 탄소 감축 성과 기반 ESG 랭킹 보드</h3>
</div>
""", unsafe_allow_html=True)


# 샘플 랭킹 데이터 생성
industries = ["전자제품", "철강", "화학", "자동차", "건설", "에너지"]
companies = ["삼성전자", "포스코", "LG화학", "현대자동차", "현대건설", "한국전력"]
ranking_data = []

for i, (ind, comp) in enumerate(zip(industries, companies)):
    # 랭킹 점수 계산 (감축률, 할당 효율성, ESG 점수 종합)
    reduction_rate = np.random.uniform(10, 30)
    allocation_efficiency = np.random.uniform(80, 150)
    esg_score = np.random.uniform(60, 95)
    
    # 종합 점수 계산
    total_score = (reduction_rate * 0.4 + 
                  (allocation_efficiency/100) * 30 + 
                  esg_score * 0.3)
    
    ranking_data.append({
        '순위': i + 1,
        '기업명': comp,
        '업종': ind,
        '감축률(%)': round(reduction_rate, 1),
        '할당효율성(%)': round(allocation_efficiency, 1),
        'ESG점수': round(esg_score, 1),
        '종합점수': round(total_score, 1)
    })

ranking_df = pd.DataFrame(ranking_data)

# 랭킹 테이블
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 업종별 ESG 랭킹")
    st.dataframe(ranking_df, use_container_width=True)

with col2:
    st.subheader("🏆 현재 기업 순위")
    current_rank = ranking_df[ranking_df['기업명'] == company_name]['순위'].iloc[0] if company_name in ranking_df['기업명'].values else "N/A"
    st.metric("현재 순위", f"{current_rank}위", "상위 20%")
    
    # ESG 등급
    if current_esg_score >= 90:
        grade = "A+"
        color = "🟢"
    elif current_esg_score >= 80:
        grade = "A"
        color = "🟢"
    elif current_esg_score >= 70:
        grade = "B+"
        color = "🟡"
    elif current_esg_score >= 60:
        grade = "B"
        color = "🟡"
    else:
        grade = "C"
        color = "🔴"
    
    st.metric("ESG 등급", f"{color} {grade}", f"{current_esg_score}점")

# 트렌드 추적 그래프
st.subheader("📈 ESG 등급 추세")
trend_data = []
for month in range(1, 13):
    trend_data.append({
        '월': f"2024-{month:02d}",
        'ESG점수': current_esg_score + np.random.normal(0, 2),
        '감축률': current_reduction_rate + np.random.normal(0, 1)
    })

trend_df = pd.DataFrame(trend_data)

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
fig_trend.add_trace(
    go.Scatter(x=trend_df['월'], y=trend_df['ESG점수'], name="ESG 점수", line=dict(color='blue')),
    secondary_y=False
)
fig_trend.add_trace(
    go.Scatter(x=trend_df['월'], y=trend_df['감축률'], name="감축률 (%)", line=dict(color='red')),
    secondary_y=True
)
fig_trend.update_layout(title="월별 ESG 점수 및 감축률 추이", height=400)
st.plotly_chart(fig_trend, use_container_width=True)

# 2. 🥈 업종별·기업별 탄소 KPI 비교 페이지
st.markdown("""
<div class="ranking-card">
    <h3>🥈 업종별·기업별 탄소 KPI 비교</h3>
</div>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">총배출량 대비 감축률</div>
                <div data-testid="metric-value">"""+f"{current_reduction_rate}%"+"""</div>
                <div data-testid="metric-delta">업종 평균 """+f"{ranking_df[ranking_df['업종'] == industry]['감축률(%)'].mean():.1f}%"+"""</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">할당 대비 잉여율</div>
                <div data-testid="metric-value">"""+f"{current_allocation_ratio}%"+"""</div>
                <div data-testid="metric-delta">"""+"탄소 여유 있음" if current_allocation_ratio > 100 else "부족"+"""</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    trading_efficiency = np.random.uniform(60, 95)
    st.markdown("""
    <div class="metric-highlight">
        <div data-testid="metric-container">
            <div data-testid="metric">
                <div data-testid="metric-label">거래 활용도</div>
                <div data-testid="metric-value">"""+f"{trading_efficiency:.1f}%"+"""</div>
                <div data-testid="metric-delta">"""+"효율적" if trading_efficiency > 80 else "개선 필요"+"""</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# KPI 비교 차트
fig_kpi = px.scatter(ranking_df, x='감축률(%)', y='ESG점수', 
                     size='종합점수', color='업종',
                     hover_name='기업명', title="감축률 vs ESG 점수 비교")
st.plotly_chart(fig_kpi, use_container_width=True)

# 3. 🥉 Gamification: ESG 등급 배지 + 소셜 공유
st.markdown("""
<div class="badge-container">
    <h3>🥉 ESG 등급 배지 + 소셜 공유</h3>
</div>
""", unsafe_allow_html=True)


# 배지 생성 함수
def create_esg_badge(grade, company_name, score):
    # 배지 이미지 생성
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 배지 디자인
    if grade == "A+":
        color = (255, 215, 0)  # Gold
        medal = "🥇"
    elif grade == "A":
        color = (192, 192, 192)  # Silver
        medal = "🥈"
    else:
        color = (205, 127, 50)  # Bronze
        medal = "🥉"
    
    # 배지 그리기
    draw.ellipse([50, 50, 350, 150], outline=color, width=5)
    draw.text((200, 80), f"{medal} ESG {grade}", fill=color, anchor="mm")
    draw.text((200, 110), company_name, fill='black', anchor="mm")
    draw.text((200, 140), f"Score: {score}", fill='black', anchor="mm")
    
    return img

# 배지 생성 및 표시
badge_img = create_esg_badge(grade, company_name, current_esg_score)

col1, col2, col3 = st.columns(3)

with col1:
    st.image(badge_img, caption=f"ESG {grade} 배지", use_container_width=True)

with col2:
    st.subheader("📊 배지 정보")
    st.write(f"**기업명**: {company_name}")
    st.write(f"**ESG 등급**: {grade}")
    st.write(f"**점수**: {current_esg_score}점")
    st.write(f"**감축률**: {current_reduction_rate}%")
    st.write(f"**업종**: {industry}")

with col3:
    st.subheader("📤 공유 기능")
    
    # 배지 다운로드
    buf = io.BytesIO()
    badge_img.save(buf, format='PNG')
    buf.seek(0)
    
    st.download_button(
        label="📄 배지 다운로드",
        data=buf.getvalue(),
        file_name=f"ESG_Badge_{company_name}_{grade}.png",
        mime="image/png"
    )
    
    # 공유 문구 생성
    share_text = f"""
🏆 {company_name} ESG 성과 공유

📊 ESG 등급: {grade} ({current_esg_score}점)
🌱 탄소 감축률: {current_reduction_rate}%
🏭 업종: {industry}

#ESG #탄소감축 #지속가능경영
    """.strip()
    
    st.text_area("📝 공유 문구", share_text, height=150)
    
    if st.button("📋 복사"):
        st.success("공유 문구가 클립보드에 복사되었습니다!")

# 4. 🧠 AI 기반 ESG 개선 시뮬레이터
st.markdown("""
<div class="simulator-container">
    <h3>🧠 AI 기반 ESG 개선 시뮬레이터</h3>
</div>
""", unsafe_allow_html=True)


# 시뮬레이터 입력
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 현재 상황")
    st.write(f"**현재 ESG 점수**: {current_esg_score}점")
    st.write(f"**현재 감축률**: {current_reduction_rate}%")
    st.write(f"**목표 ESG 점수**: {target_esg_score}점")
    st.write(f"**목표 감축률**: {target_reduction_rate}%")

with col2:
    st.subheader("🎯 개선 목표")
    improvement_needed = target_esg_score - current_esg_score
    reduction_needed = target_reduction_rate - current_reduction_rate
    
    st.metric("필요 ESG 점수 상승", f"+{improvement_needed}점")
    st.metric("필요 감축률 상승", f"+{reduction_needed}%")

# AI 시뮬레이션 실행
if st.button("🤖 AI 시뮬레이션 실행", type="primary"):
    st.subheader("📊 AI 분석 결과")
    
    # 시뮬레이션 결과 생성
    scenarios = [
        {
            "전략": "에너지 효율 개선",
            "투자비용": f"{improvement_needed * 2}억원",
            "예상효과": f"ESG +{improvement_needed * 0.3:.1f}점",
            "소요기간": "6개월",
            "성공확률": "85%"
        },
        {
            "전략": "재생에너지 전환",
            "투자비용": f"{improvement_needed * 5}억원",
            "예상효과": f"ESG +{improvement_needed * 0.5:.1f}점",
            "소요기간": "12개월",
            "성공확률": "75%"
        },
        {
            "전략": "배출권 거래 최적화",
            "투자비용": f"{improvement_needed * 1}억원",
            "예상효과": f"ESG +{improvement_needed * 0.2:.1f}점",
            "소요기간": "3개월",
            "성공확률": "90%"
        }
    ]
    
    scenario_df = pd.DataFrame(scenarios)
    st.dataframe(scenario_df, use_container_width=True)
    
    # 추천 전략
    st.subheader("💡 AI 추천 전략")
    best_scenario = scenarios[0]  # 가장 높은 성공확률
    
    st.markdown(f"""
    **🎯 최적 전략**: {best_scenario['전략']}
    
    - **투자비용**: {best_scenario['투자비용']}
    - **예상효과**: {best_scenario['예상효과']}
    - **소요기간**: {best_scenario['소요기간']}
    - **성공확률**: {best_scenario['성공확률']}
    """)
    
    # 시각화
    fig_scenario = px.bar(scenario_df, x='전략', y='성공확률', 
                         title="전략별 성공확률 비교",
                         color='성공확률', color_continuous_scale='viridis')
    st.plotly_chart(fig_scenario, use_container_width=True)

# 사용 가이드
st.markdown("## 📖 사용 가이드")

st.markdown("""
### 🎯 **1단계: 현황 파악**
왼쪽 사이드바의 **"현황 대시보드"**를 클릭하여 현재 탄소배출량과 배출권 시장 상황을 파악하세요.

### 💡 **2단계: 전략 수립**
**"구매 전략 대시보드"**에서 AI 기반 구매 전략과 투자 방향을 확인하세요.

### 📈 **3단계: 실행 및 모니터링**
수립된 전략을 실행하고 지속적으로 모니터링하여 최적화하세요.
""")


# 플로팅 챗봇 버튼 제거됨

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; margin-top: 50px;'>
        <p>🌍 탄소배출권 통합 관리 시스템 | Built with Streamlit & Plotly</p>
        <p>실시간 데이터 기반 종합 탄소배출권 관리 솔루션</p>
    </div>
    """, 
    unsafe_allow_html=True
) 