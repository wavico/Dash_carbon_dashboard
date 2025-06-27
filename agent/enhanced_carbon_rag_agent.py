"""
향상된 탄소 RAG 에이전트
고급 데이터 전처리, 쿼리 분석, 시각화 엔진을 통합한 AI 에이전트
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# .env 파일 로드 시도
try:
    load_dotenv()
    # .env 파일 로드가 실패할 경우를 대비한 직접 설정
    if not os.getenv('UPSTAGE_API_KEY'):
        # .env 파일에서 직접 읽기
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
except Exception as e:
    print(f"환경변수 로드 중 오류: {e}")
    # 직접 설정 (임시)
    os.environ['UPSTAGE_API_KEY'] = 'up_Tfh3KhtojqHp2MascmzOv3IG4lDu0'
from typing import List, Dict, Tuple, Optional, Any
from langchain_upstage import ChatUpstage
from langchain.schema import HumanMessage, SystemMessage
import warnings

# 새로 구현한 모듈들 import
from .data_preprocessor import DataPreprocessor
from .query_analyzer import QueryAnalyzer, QueryIntent
from .visualization_engine import VisualizationEngine
from .metadata_manager import MetadataManager
from .code_executor import SafeCodeExecutor

warnings.filterwarnings('ignore')

# 환경변수 확인 및 설정
if not os.getenv('UPSTAGE_API_KEY'):
    print("🔧 환경변수를 직접 설정합니다...")
    os.environ['UPSTAGE_API_KEY'] = 'up_Tfh3KhtojqHp2MascmzOv3IG4lDu0'

class EnhancedCarbonRAGAgent:
    """향상된 탄소 데이터 RAG 에이전트"""
    
    _instance = None
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(EnhancedCarbonRAGAgent, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """에이전트 초기화"""
        if hasattr(self, '_initialized'):
            return
            
        # API 키 확인
        self.api_key = os.getenv('UPSTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
        
        # LLM 초기화
        self.llm = ChatUpstage(
            api_key=self.api_key,
            model="solar-1-mini-chat"
        )
        
        # 데이터 폴더 경로
        self.data_folder = "data"
        
        # 고급 시스템 컴포넌트들 초기화
        self.data_preprocessor = DataPreprocessor(self.data_folder)
        self.query_analyzer = QueryAnalyzer()
        self.visualization_engine = VisualizationEngine()
        self.metadata_manager = MetadataManager("agent/metadata.json")
        self.code_executor = SafeCodeExecutor()
        
        # 데이터 로드 및 전처리
        self._load_and_process_data()
        
        self._initialized = True
        print("✅ 향상된 탄소 RAG 에이전트가 초기화되었습니다.")
    
    def _load_and_process_data(self):
        """데이터 로드 및 전처리"""
        print("🔄 데이터 분석 및 전처리 중...")
        
        # 1. 모든 데이터셋 분석
        self.dataset_info = self.data_preprocessor.analyze_all_datasets()
        
        # 2. 데이터 표준화 및 통합
        self.unified_data = self.data_preprocessor.standardize_data()
        
        # 3. 메타데이터 생성
        self.metadata_manager.analyze_and_create_metadata(self.data_preprocessor.datasets)
        
        # 4. 데이터 요약 정보 생성
        self.data_summary = self.data_preprocessor.get_data_summary()
        
        print(f"✅ 데이터 전처리 완료:")
        print(f"   - 총 {self.data_summary['total_datasets']}개 데이터셋 로드")
        if self.unified_data is not None:
            print(f"   - 통합 데이터: {self.unified_data.shape[0]}행 × {self.unified_data.shape[1]}열")
            print(f"   - 연도 범위: {self.data_summary['year_range']}")
    
    def ask(self, question: str) -> Tuple[str, Optional[str]]:
        """
        질문에 대한 답변 및 시각화 생성
        
        Args:
            question: 사용자 질문
            
        Returns:
            (답변 텍스트, 시각화 이미지 base64)
        """
        try:
            print(f"🎯 질문 처리 시작: '{question}'")
            
            # 1. 질문 의도 분석
            intent = self.query_analyzer.analyze_query(question)
            print(f"🔍 질문 분석 완료: {intent.query_type.value} (신뢰도: {intent.confidence:.2f})")
            print(f"📅 추출된 연도: {intent.years}")
            print(f"🏷️ 추출된 엔티티: {intent.entities}")
            
            # 2. 시각화 필요성 판단
            needs_viz = self.query_analyzer.needs_visualization(question)
            print(f"📊 시각화 필요: {needs_viz}")
            
            # 3. 데이터 필터링 및 분석
            analysis_result = self._perform_data_analysis(intent)
            print(f"📈 분석 결과 성공: {analysis_result.get('success', False)}")
            if 'data' in analysis_result:
                print(f"📊 분석된 데이터 크기: {len(analysis_result['data']) if analysis_result['data'] is not None else 0}")
            
            # 4. 시각화 생성 (필요한 경우만)
            visualization = None
            if needs_viz:
                print("🎨 시각화 생성 시작...")
                visualization = self._create_visualization(intent, analysis_result)
                if visualization:
                    print("✅ 시각화 생성 완료")
                else:
                    print("⚠️ 시각화 생성 실패")
            else:
                print("ℹ️ 텍스트 답변만 제공")
            
            # 5. 답변 생성
            answer = self._generate_answer(question, intent, analysis_result)
            
            return answer, visualization
            
        except Exception as e:
            error_msg = f"❌ 처리 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg, None
    
    def _perform_data_analysis(self, intent: QueryIntent) -> Dict[str, Any]:
        """질문 의도를 바탕으로 데이터 분석 수행"""
        if self.unified_data is None or self.unified_data.empty:
            return {"error": "분석할 데이터가 없습니다."}
        
        try:
            # 코드 생성 및 실행
            context = {"unified_data": self.unified_data}
            
            # 질문 의도에 따른 분석 코드 생성
            analysis_code = self.code_executor.generate_analysis_code(
                intent, 
                list(self.unified_data.columns)
            )
            
            # 코드 실행
            success, result, output = self.code_executor.execute_code(analysis_code, context)
            
            if success and result is not None:
                return {
                    "success": True,
                    "data": result,
                    "output": output,
                    "code": analysis_code
                }
            else:
                # 실패 시 기본 분석 수행
                return self._fallback_analysis(intent)
                
        except Exception as e:
            print(f"분석 오류: {e}")
            return self._fallback_analysis(intent)
    
    def _fallback_analysis(self, intent: QueryIntent) -> Dict[str, Any]:
        """기본 분석 (코드 실행 실패 시)"""
        try:
            # 국가 온실가스 인벤토리 데이터셋만 사용
            inventory_dataset = None
            for dataset_name, df in self.data_preprocessor.datasets.items():
                if '국가 온실가스 인벤토리' in dataset_name:
                    inventory_dataset = df
                    print(f"📊 국가 온실가스 인벤토리 데이터셋 사용: {dataset_name}")
                    break
            
            if inventory_dataset is None or inventory_dataset.empty:
                return {"error": "국가 온실가스 인벤토리 데이터를 찾을 수 없습니다."}
            
            # 연도 필터링
            if intent.years:
                # 첫 번째 컬럼이 연도 (이미 data_preprocessor에서 확인됨)
                year_mask = inventory_dataset.iloc[:, 0].isin(intent.years)
                filtered_data = inventory_dataset[year_mask].copy()
                print(f"📅 연도 필터링: {intent.years} → {len(filtered_data)}개 레코드")
            else:
                filtered_data = inventory_dataset.copy()
            
            # 결과 데이터 준비
            result_data = []
            
            # 질문 타입별 분석
            if intent.query_type.value == 'comparison' and intent.years:
                # 연도별 비교: 각 연도의 총배출량 (두 번째 컬럼)
                for year in intent.years:
                    year_row = inventory_dataset[inventory_dataset.iloc[:, 0] == year]
                    if not year_row.empty:
                        total_emission = year_row.iloc[0, 1]  # 두 번째 컬럼이 총배출량
                        result_data.append({
                            'year': year,
                            'value': total_emission
                        })
                        print(f"📈 {year}년 총배출량: {total_emission:,.1f} (백만톤 CO₂)")
                
                result = pd.DataFrame(result_data)
                        
            elif intent.query_type.value == 'trend':
                # 추세 분석: 모든 연도의 총배출량
                for _, row in inventory_dataset.iterrows():
                    year = row.iloc[0]
                    total_emission = row.iloc[1]
                    if pd.notna(year) and pd.notna(total_emission):
                        result_data.append({
                            'year': int(year),
                            'value': float(total_emission)
                        })
                
                result = pd.DataFrame(result_data).sort_values('year')
            else:
                # 기본: 요청된 연도들의 데이터
                for _, row in filtered_data.iterrows():
                    year = row.iloc[0]
                    total_emission = row.iloc[1]
                    if pd.notna(year) and pd.notna(total_emission):
                        result_data.append({
                            'year': int(year),
                            'value': float(total_emission)
                        })
                
                result = pd.DataFrame(result_data)
            
            if result.empty:
                return {"error": "요청한 연도의 데이터를 찾을 수 없습니다."}
            
            return {
                "success": True,
                "data": result,
                "output": f"국가 온실가스 인벤토리 분석 완료 - 총배출량 기준 (백만톤 CO₂)"
            }
            
        except Exception as e:
            print(f"기본 분석 오류: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"기본 분석 실패: {e}"}
    
    def _create_visualization(self, intent: QueryIntent, analysis_result: Dict[str, Any]) -> Optional[str]:
        """분석 결과를 바탕으로 시각화 생성"""
        if not analysis_result.get("success") or analysis_result.get("data") is None:
            return None
        
        try:
            data = analysis_result["data"]
            
            # 시각화 매개변수 생성
            viz_params = self.query_analyzer.suggest_visualization_params(intent)
            
            # 차트 제목 생성
            title = self._generate_chart_title(intent)
            
            # 시각화 생성
            visualization = self.visualization_engine.create_visualization(
                data=data,
                chart_type=intent.chart_type.value,
                title=title,
                params=viz_params
            )
            
            return visualization
            
        except Exception as e:
            print(f"시각화 생성 오류: {e}")
            return None
    
    def _generate_chart_title(self, intent: QueryIntent) -> str:
        """차트 제목 생성"""
        if intent.query_type.value == 'comparison' and intent.years:
            if len(intent.years) == 2:
                return f"{intent.years[0]}년과 {intent.years[1]}년 배출량 비교"
            else:
                return f"{min(intent.years)}-{max(intent.years)}년 배출량 비교"
        elif intent.query_type.value == 'trend':
            return "연도별 배출량 변화 추이"
        elif intent.query_type.value == 'ranking':
            return "분야별 배출량 순위"
        else:
            return "배출량 분석 결과"
    
    def _generate_answer(self, question: str, intent: QueryIntent, analysis_result: Dict[str, Any]) -> str:
        """분석 결과를 바탕으로 자연어 답변 생성"""
        try:
            # 시스템 프롬프트
            system_prompt = f"""
당신은 온실가스 배출량 데이터 전문 분석가입니다.

질문: {question}
질문 타입: {intent.query_type.value}
신뢰도: {intent.confidence:.2f}
추출된 연도: {intent.years}
관련 분야: {intent.entities}
메트릭: {intent.metrics}

분석 결과:
{analysis_result.get('output', '분석 결과 없음')}

위 정보를 바탕으로 다음 요구사항에 맞춰 답변해주세요:

1. 질문에 직접적으로 답변
2. 구체적인 수치 포함
3. 간단한 해석 및 인사이트 제공
4. 한국어로 친근하게 설명
5. 3-5문장으로 간결하게 작성

데이터 출처: 환경부, 한국거래소, 한국에너지공단 등 공공기관
"""
            
            # LLM으로 답변 생성
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=question)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            # LLM 실패 시 기본 답변
            return self._generate_fallback_answer(question, analysis_result)
    
    def _generate_fallback_answer(self, question: str, analysis_result: Dict[str, Any]) -> str:
        """기본 답변 생성 (LLM 실패 시)"""
        if analysis_result.get("error"):
            return f"죄송합니다. 데이터 분석 중 오류가 발생했습니다: {analysis_result['error']}"
        
        if analysis_result.get("data") is not None:
            data = analysis_result["data"]
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                # 기본적인 통계 정보 제공
                if 'value' in data.columns:
                    total = data['value'].sum()
                    avg = data['value'].mean()
                    return f"분석 결과, 총 배출량은 {total:,.0f}이며, 평균은 {avg:,.0f}입니다. 자세한 내용은 위의 그래프를 참고해주세요."
                else:
                    return f"데이터 분석이 완료되었습니다. 총 {len(data)}개의 레코드가 있습니다."
            else:
                return "데이터가 비어있거나 분석할 수 없는 형태입니다."
        
        return "죄송합니다. 해당 질문에 대한 분석을 완료하지 못했습니다."
    
    def get_available_data_info(self) -> str:
        """사용 가능한 데이터 정보 반환"""
        info_parts = ["📊 **사용 가능한 데이터:**\n"]
        
        for name, info in self.dataset_info.items():
            info_parts.append(f"**{name}**")
            info_parts.append(f"- {info.description}")
            info_parts.append(f"- 크기: {info.shape[0]}행 × {info.shape[1]}열")
            if info.has_year_columns:
                years = [str(col) for col in info.year_columns[:5]]  # 처음 5개만
                info_parts.append(f"- 연도: {', '.join(years)}...")
            info_parts.append("")
        
        # 통합 데이터 정보
        if self.unified_data is not None:
            info_parts.append("**📈 통합 분석 데이터:**")
            info_parts.append(f"- 전체 레코드: {len(self.unified_data):,}개")
            info_parts.append(f"- 연도 범위: {self.data_summary['year_range']}")
            info_parts.append(f"- 데이터셋 수: {self.data_summary['datasets_in_unified']}개")
        
        return "\n".join(info_parts)
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 정보 반환"""
        return {
            "datasets_loaded": len(self.dataset_info),
            "unified_data_size": len(self.unified_data) if self.unified_data is not None else 0,
            "metadata_available": len(self.metadata_manager.metadata),
            "execution_history": self.code_executor.get_execution_summary(),
            "data_summary": self.data_summary
        }
    
    def debug_query(self, question: str) -> Dict[str, Any]:
        """질문 디버깅 정보 제공"""
        intent = self.query_analyzer.analyze_query(question)
        
        return {
            "question": question,
            "intent": {
                "query_type": intent.query_type.value,
                "chart_type": intent.chart_type.value,
                "years": intent.years,
                "entities": intent.entities,
                "metrics": intent.metrics,
                "confidence": intent.confidence
            },
            "suggested_params": self.query_analyzer.suggest_visualization_params(intent),
            "available_data": list(self.dataset_info.keys())
        } 