# 🌍 탄소배출량 및 배출권 현황 대시보드

한국의 탄소배출량과 배출권 거래 현황을 시각화하는 인터랙티브 웹 대시보드입니다. Plotly Dash를 기반으로 구축되었으며, 실시간 데이터 분석과 다양한 차트를 제공합니다.

## 📊 주요 기능

- **🔍 인터랙티브 필터링**: 연도/월별 데이터 필터링
- **📈 실시간 지표**: 탄소배출권 보유수량 및 현재 배출량 게이지
- **🗺️ 지역별 분석**: 전국 17개 시도별 CO₂ 농도 지도 시각화
- **📊 다양한 차트**: 바차트, 트리맵, 시계열 분석 등
- **💹 시장 데이터**: KAU24 시가 및 거래량 추이 분석
- **🏭 기업별 현황**: 주요 기업별 탄소배출권 할당량 분석

## 🏗️ 프로젝트 구조

```
dash_scripts/
├── dash_carbon_dashboard.py      # 🎯 메인 대시보드 (독립 실행 가능)
├── dash_data_manager.py          # 📊 엔터프라이즈 데이터 관리자
├── dash_enterprise_config.py     # ⚙️ 엔터프라이즈 설정
└── dash_enterprise_main.py       # 🏢 엔터프라이즈 메인 애플리케이션
```

### 파일별 설명

- **`dash_carbon_dashboard.py`**: 독립적으로 실행 가능한 기본 대시보드
- **`dash_data_manager.py`**: Redis 캐싱 및 실시간 데이터 관리 기능
- **`dash_enterprise_config.py`**: 엔터프라이즈 인증 및 보안 설정
- **`dash_enterprise_main.py`**: 고급 기능이 포함된 엔터프라이즈 버전

## 🚀 실행 방법

### 1단계: 프로젝트 클론

```bash
# Git 저장소 클론
git clone <repository-url>
cd streamlit-dashboard
```

### 2단계: 가상환경 설정 (권장)

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3단계: 의존성 설치

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 4단계: 대시보드 실행

```bash
# 기본 대시보드 실행
python dash_scripts/dash_carbon_dashboard.py
```

### 5단계: 브라우저에서 접속

대시보드가 성공적으로 실행되면 터미널에 다음과 같은 메시지가 표시됩니다:

```
Dash is running on http://0.0.0.0:8050/
 * Serving Flask app 'dash_carbon_dashboard'
 * Debug mode: on
```

브라우저에서 다음 URL로 접속하세요:
- **http://localhost:8050**
- **http://127.0.0.1:8050**

## 📋 필요 패키지

```
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
numpy>=1.24.0
dash>=2.14.0
dash-bootstrap-components>=1.5.0
```

## 🎯 사용 방법

### 기본 조작

1. **연도 선택**: 상단 슬라이더로 2020-2024년 선택
2. **월 선택**: 월별 데이터 필터링 (1-12월)
3. **차트 상호작용**: 마우스 오버, 줌, 팬 등 지원

### 주요 차트 설명

- **게이지 차트**: 탄소배출권 보유수량과 현재 배출량 실시간 표시
- **지도 차트**: 전국 17개 시도별 CO₂ 농도 분포
- **바 차트**: 연도별 총배출량 vs 특정산업배출량 비교
- **콤보 차트**: KAU24 시가와 거래량 월별 추이
- **트리맵**: 업종별/기업별 탄소배출권 할당량 비율
- **시계열 차트**: 주요 지역별 CO₂ 농도 변화 추이

## 🛠️ 문제 해결

### 일반적인 오류 해결

1. **포트 충돌 오류**
   ```bash
   # 다른 포트로 실행
   # dash_carbon_dashboard.py 파일에서 port=8051로 변경
   ```

2. **패키지 누락 오류**
   ```bash
   # 개별 패키지 설치
   pip install dash plotly pandas numpy
   ```

3. **방화벽 경고**
   - Windows에서 방화벽 경고 시 "액세스 허용" 클릭

### 서버 종료

```bash
# 터미널에서 Ctrl + C 입력
```

## 🔧 개발 환경

- **Python**: 3.8+
- **Dash**: 2.14.0+
- **Plotly**: 5.15.0+
- **Pandas**: 1.5.0+
- **NumPy**: 1.24.0+

## 📈 데이터 소스

현재 버전은 시연용 샘플 데이터를 사용합니다:
- 지역별 CO₂ 농도 데이터 (17개 시도)
- 연도별 탄소배출량 통계 (2020-2024)
- KAU24 시장 데이터 (시가/거래량)
- 주요 기업 배출권 할당량 데이터

## 🚀 고급 기능 (Enterprise)

엔터프라이즈 버전 사용 시 추가 기능:
- Redis 캐싱으로 성능 최적화
- 실시간 데이터 업데이트
- 사용자 인증 및 권한 관리
- 데이터 내보내기 기능
- 모니터링 및 로깅

```bash
# 엔터프라이즈 버전 실행 (Redis 설정 필요)
python dash_scripts/dash_enterprise_main.py
```

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 이슈를 등록해 주세요.

---

**🌍 지속 가능한 미래를 위한 탄소 데이터 시각화** | Built with ❤️ using Plotly Dash 