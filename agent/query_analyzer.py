"""
스마트 쿼리 분석기
사용자 질문을 분석해서 의도를 파악하는 NLP 모듈
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class QueryType(Enum):
    """질문 타입 열거형"""
    COMPARISON = "comparison"  # 비교
    TREND = "trend"  # 추세
    RANKING = "ranking"  # 순위
    STATISTICS = "statistics"  # 통계
    SPECIFIC_VALUE = "specific_value"  # 특정 값 조회
    CORRELATION = "correlation"  # 상관관계
    PREDICTION = "prediction"  # 예측
    SUMMARY = "summary"  # 요약
    UNKNOWN = "unknown"  # 알 수 없음

class ChartType(Enum):
    """차트 타입 열거형"""
    LINE = "line"  # 선 그래프
    BAR = "bar"  # 막대 그래프
    PIE = "pie"  # 파이 차트
    SCATTER = "scatter"  # 산점도
    HISTOGRAM = "histogram"  # 히스토그램
    HEATMAP = "heatmap"  # 히트맵
    BOX = "box"  # 박스플롯
    AREA = "area"  # 영역 차트

@dataclass
class QueryIntent:
    """질문 의도 분석 결과"""
    query_type: QueryType
    chart_type: ChartType
    years: List[int]
    entities: List[str]  # 분야, 기업 등
    metrics: List[str]  # 배출량, 할당량 등
    comparison_items: List[str]
    time_period: Optional[Tuple[int, int]]
    aggregation: Optional[str]  # sum, avg, max, min
    confidence: float

class QueryAnalyzer:
    """질문 의도 분석 및 분류 클래스"""
    
    def __init__(self):
        """쿼리 분석기 초기화"""
        self.year_pattern = r'(\d{4})'
        self.comparison_keywords = [
            '비교', '차이', '대비', 'vs', '와', '과', '보다', '대조',
            '비교해', '차이점', '차이는', '비교하면'
        ]
        self.trend_keywords = [
            '추이', '변화', '트렌드', '경향', '증가', '감소', '변동',
            '추세', '흐름', '패턴', '변화량', '증감'
        ]
        self.ranking_keywords = [
            '순위', '많은', '적은', '높은', '낮은', '최대', '최소',
            '가장', '상위', '하위', '1위', '톱', '랭킹'
        ]
        self.statistics_keywords = [
            '평균', '총합', '합계', '전체', '총', '평균적으로',
            '통계', '분포', '비율', '퍼센트', '%'
        ]
        self.correlation_keywords = [
            '관계', '상관관계', '연관', '영향', '관련',
            '상관성', '연관성', '관계성'
        ]
        
        # 분야/산업 키워드
        self.sector_keywords = {
            '에너지': ['에너지', '전력', '발전', '연료'],
            '산업': ['산업', '제조', '공장', '생산'],
            '수송': ['수송', '교통', '운송', '자동차', '항공', '선박'],
            '건물': ['건물', '주거', '상업', '난방', '냉방'],
            '농업': ['농업', '축산', '임업', '농림'],
            '폐기물': ['폐기물', '쓰레기', '폐기', '재활용']
        }
        
        # 메트릭 키워드
        self.metric_keywords = {
            '배출량': ['배출량', '배출', '방출', 'CO2', '온실가스', 'GHG'],
            '할당량': ['할당량', '할당', '배정'],
            '거래량': ['거래량', '거래', '매매'],
            '감축량': ['감축량', '감축', '절약', '저감']
        }
    
    def analyze_query(self, query: str) -> QueryIntent:
        """질문 분석하여 의도 파악"""
        query = query.strip()
        
        # 연도 추출
        years = self._extract_years(query)
        
        # 질문 타입 분류
        query_type = self._classify_query_type(query)
        
        # 차트 타입 결정
        chart_type = self._determine_chart_type(query_type, years)
        
        # 엔티티 추출 (분야, 기업 등)
        entities = self._extract_entities(query)
        
        # 메트릭 추출
        metrics = self._extract_metrics(query)
        
        # 비교 항목 추출
        comparison_items = self._extract_comparison_items(query)
        
        # 시간 범위 결정
        time_period = self._determine_time_period(years)
        
        # 집계 방법 결정
        aggregation = self._determine_aggregation(query)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(query, query_type, years, entities, metrics)
        
        return QueryIntent(
            query_type=query_type,
            chart_type=chart_type,
            years=years,
            entities=entities,
            metrics=metrics,
            comparison_items=comparison_items,
            time_period=time_period,
            aggregation=aggregation,
            confidence=confidence
        )
    
    def _extract_years(self, query: str) -> List[int]:
        """질문에서 연도 추출"""
        years = []
        matches = re.findall(self.year_pattern, query)
        for match in matches:
            year = int(match)
            if 1990 <= year <= 2030:  # 합리적인 연도 범위
                years.append(year)
        return sorted(list(set(years)))
    
    def _classify_query_type(self, query: str) -> QueryType:
        """질문 타입 분류"""
        query_lower = query.lower()
        
        # 비교 질문 검사
        if any(keyword in query_lower for keyword in self.comparison_keywords):
            return QueryType.COMPARISON
        
        # 추세 질문 검사
        if any(keyword in query_lower for keyword in self.trend_keywords):
            return QueryType.TREND
        
        # 순위 질문 검사
        if any(keyword in query_lower for keyword in self.ranking_keywords):
            return QueryType.RANKING
        
        # 통계 질문 검사
        if any(keyword in query_lower for keyword in self.statistics_keywords):
            return QueryType.STATISTICS
        
        # 상관관계 질문 검사
        if any(keyword in query_lower for keyword in self.correlation_keywords):
            return QueryType.CORRELATION
        
        # 특정 값 조회 (숫자나 "얼마" 포함)
        if re.search(r'얼마|몇|수치|값|량', query_lower):
            return QueryType.SPECIFIC_VALUE
        
        return QueryType.SUMMARY
    
    def _determine_chart_type(self, query_type: QueryType, years: List[int]) -> ChartType:
        """질문 타입과 연도 정보를 바탕으로 차트 타입 결정"""
        if query_type == QueryType.TREND:
            return ChartType.LINE
        elif query_type == QueryType.COMPARISON:
            if len(years) > 1:
                return ChartType.BAR  # 연도별 비교
            else:
                return ChartType.BAR  # 항목별 비교
        elif query_type == QueryType.RANKING:
            return ChartType.BAR
        elif query_type == QueryType.STATISTICS:
            if len(years) > 3:
                return ChartType.LINE
            else:
                return ChartType.PIE
        elif query_type == QueryType.CORRELATION:
            return ChartType.SCATTER
        else:
            return ChartType.BAR  # 기본값
    
    def _extract_entities(self, query: str) -> List[str]:
        """질문에서 분야/산업 엔티티 추출"""
        entities = []
        query_lower = query.lower()
        
        for sector, keywords in self.sector_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                entities.append(sector)
        
        return entities
    
    def _extract_metrics(self, query: str) -> List[str]:
        """질문에서 메트릭 추출"""
        metrics = []
        query_lower = query.lower()
        
        for metric, keywords in self.metric_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                metrics.append(metric)
        
        # 기본값으로 배출량 추가 (명시되지 않은 경우)
        if not metrics:
            metrics.append('배출량')
        
        return metrics
    
    def _extract_comparison_items(self, query: str) -> List[str]:
        """비교 항목 추출"""
        comparison_items = []
        
        # "A와 B 비교" 패턴 찾기
        patterns = [
            r'(\w+)와\s*(\w+)',
            r'(\w+)과\s*(\w+)',
            r'(\w+)\s*vs\s*(\w+)',
            r'(\w+)\s*대비\s*(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                comparison_items.extend(match)
        
        return comparison_items
    
    def _determine_time_period(self, years: List[int]) -> Optional[Tuple[int, int]]:
        """시간 범위 결정"""
        if len(years) >= 2:
            return (min(years), max(years))
        elif len(years) == 1:
            # 단일 연도인 경우 전후 몇 년 포함
            year = years[0]
            return (year - 2, year + 2)
        else:
            # 연도가 없는 경우 전체 범위
            return (2017, 2021)  # 데이터 범위에 맞춤
    
    def _determine_aggregation(self, query: str) -> Optional[str]:
        """집계 방법 결정"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['평균', 'average', 'avg']):
            return 'mean'
        elif any(word in query_lower for word in ['총', '합계', '전체', 'total', 'sum']):
            return 'sum'
        elif any(word in query_lower for word in ['최대', '최고', 'max', 'maximum']):
            return 'max'
        elif any(word in query_lower for word in ['최소', '최저', 'min', 'minimum']):
            return 'min'
        else:
            return 'sum'  # 기본값
    
    def _calculate_confidence(self, query: str, query_type: QueryType, 
                            years: List[int], entities: List[str], 
                            metrics: List[str]) -> float:
        """분석 결과의 신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도
        
        # 연도가 명확히 지정된 경우
        if years:
            confidence += 0.2
        
        # 분야가 명확히 지정된 경우
        if entities:
            confidence += 0.2
        
        # 메트릭이 명확한 경우
        if metrics and '배출량' in metrics:
            confidence += 0.1
        
        # 질문 타입이 명확한 경우
        if query_type != QueryType.UNKNOWN:
            confidence += 0.1
        
        # 질문 길이가 적절한 경우
        if 5 <= len(query.split()) <= 20:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_pandas_query(self, intent: QueryIntent, 
                            available_columns: List[str]) -> str:
        """의도를 바탕으로 pandas 쿼리 생성"""
        query_parts = []
        
        # 연도 필터
        if intent.years:
            if len(intent.years) == 1:
                query_parts.append(f"year == {intent.years[0]}")
            else:
                min_year, max_year = min(intent.years), max(intent.years)
                query_parts.append(f"year >= {min_year} and year <= {max_year}")
        
        # 분야 필터
        if intent.entities:
            entity_conditions = []
            for entity in intent.entities:
                # 메타 컬럼에서 해당 분야 찾기
                for col in available_columns:
                    if 'meta_' in col and entity in col.lower():
                        entity_conditions.append(f"{col}.str.contains('{entity}', na=False)")
            
            if entity_conditions:
                query_parts.append(f"({' or '.join(entity_conditions)})")
        
        return ' and '.join(query_parts) if query_parts else ""
    
    def suggest_visualization_params(self, intent: QueryIntent) -> Dict[str, Any]:
        """시각화 매개변수 제안"""
        params = {
            'chart_type': intent.chart_type.value,
            'title': self._generate_chart_title(intent),
            'x_axis': 'year' if intent.query_type == QueryType.TREND else 'category',
            'y_axis': 'value',
            'aggregation': intent.aggregation or 'sum'
        }
        
        # 차트별 특별 설정
        if intent.chart_type == ChartType.PIE:
            params['show_percentages'] = True
        elif intent.chart_type == ChartType.LINE:
            params['show_markers'] = True
            params['line_style'] = '-'
        elif intent.chart_type == ChartType.BAR:
            params['orientation'] = 'vertical'
        
        return params
    
    def _generate_chart_title(self, intent: QueryIntent) -> str:
        """차트 제목 생성"""
        if intent.query_type == QueryType.COMPARISON and intent.years:
            if len(intent.years) == 2:
                return f"{intent.years[0]}년과 {intent.years[1]}년 비교"
        elif intent.query_type == QueryType.TREND:
            return "연도별 변화 추이"
        elif intent.query_type == QueryType.RANKING:
            return "순위별 현황"
        
        return "데이터 분석 결과"
    
    def needs_visualization(self, question: str) -> bool:
        """질문이 시각화를 필요로 하는지 판단"""
        # 차트 생성 키워드 체크
        chart_keywords = [
            '그래프', '차트', '그려줘', '그려주세요', '시각화', 
            '막대그래프', '선그래프', '파이차트', '도표', '도식',
            '보여줘', '보여주세요', '그림', '차트로', '그래프로',
            '표현해줘', '표현해주세요', '비교해줘', '비교해주세요'
        ]
        
        question_lower = question.lower()
        
        # 키워드가 포함된 경우에만 시각화 생성
        has_chart_keyword = any(keyword in question_lower for keyword in chart_keywords)
        
        print(f"🔍 시각화 키워드 검사: '{question}'")
        print(f"   - 발견된 키워드: {[kw for kw in chart_keywords if kw in question_lower]}")
        print(f"   - 키워드 기반 시각화 필요: {has_chart_keyword}")
        
        # 키워드가 있으면 바로 True 반환
        if has_chart_keyword:
            print(f"   ✅ 시각화 키워드 발견으로 시각화 생성")
            return True
        
        # 키워드가 없는 경우에만 패턴 매칭 확인
        comparison_patterns = [
            r'(\d{4})년.*(\d{4})년.*비교',
            r'비교.*(\d{4})년.*(\d{4})년',
            r'(\d{4}).*vs.*(\d{4})',
            r'(\d{4}).*대비.*(\d{4})',
            r'차이.*(\d{4}).*(\d{4})'
        ]
        
        trend_patterns = [
            r'추이', r'변화', r'트렌드', r'경향',
            r'증가', r'감소', r'변동'
        ]
        
        ranking_patterns = [
            r'순위', r'랭킹', r'많은', r'적은',
            r'최대', r'최소', r'상위', r'하위'
        ]
        
        # 패턴 매칭
        for pattern in comparison_patterns:
            if re.search(pattern, question):
                print(f"   ✅ 비교 패턴 발견으로 시각화 생성")
                return True
                
        for pattern in trend_patterns:
            if re.search(pattern, question):
                print(f"   ✅ 트렌드 패턴 발견으로 시각화 생성")
                return True
                
        for pattern in ranking_patterns:
            if re.search(pattern, question):
                print(f"   ✅ 순위 패턴 발견으로 시각화 생성")
                return True
        
        print(f"   ❌ 시각화 키워드나 패턴을 찾지 못함")
        return False 