"""
Carbon Data Analysis RAG Agent
탄소 배출 데이터 분석을 위한 RAG 에이전트

이 모듈은 /data 폴더의 모든 CSV 파일을 분석하고
사용자의 질문에 대해 데이터 기반 답변을 제공합니다.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain_upstage import ChatUpstage
from langchain_teddynote.messages import AgentStreamParser
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CarbonDataRAGAgent:
    """탄소 데이터 분석을 위한 RAG 에이전트 클래스"""
    
    def __init__(self, data_folder_path: str = "data"):
        """
        RAG 에이전트 초기화
        
        Args:
            data_folder_path: 데이터 폴더 경로
        """
        self.data_folder_path = data_folder_path
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.agent = None
        self.stream_parser = AgentStreamParser()
        self.unified_df = None
        
        # 환경 변수 로드
        load_dotenv()
        
        # 데이터 로드 및 전처리
        self._load_all_data()
        self._setup_agent()
    
    def _load_all_data(self) -> None:
        """data 폴더의 모든 CSV 파일을 로드하고 전처리"""
        try:
            # 데이터 폴더 확인
            if not os.path.exists(self.data_folder_path):
                st.error(f"데이터 폴더를 찾을 수 없습니다: {self.data_folder_path}")
                return
            
            # CSV 파일 목록 가져오기
            csv_files = [f for f in os.listdir(self.data_folder_path) if f.endswith('.csv')]
            
            if not csv_files:
                st.warning("데이터 폴더에서 CSV 파일을 찾을 수 없습니다.")
                return
            
            # 각 CSV 파일 로드
            for csv_file in csv_files:
                file_path = os.path.join(self.data_folder_path, csv_file)
                try:
                    # 파일명에서 확장자 제거하여 키로 사용
                    file_key = os.path.splitext(csv_file)[0]
                    
                    # 인코딩 시도 (euc-kr 우선, 실패시 utf-8)
                    try:
                        df = pd.read_csv(file_path, encoding='euc-kr')
                    except UnicodeDecodeError:
                        df = pd.read_csv(file_path, encoding='utf-8')
                    
                    # 특별한 전처리가 필요한 파일들 처리
                    if "국가 온실가스 인벤토리" in csv_file:
                        df = self._preprocess_inventory_data(df)
                    elif "기업_규모_지역별" in csv_file:
                        # Excel 파일인 경우 스킵 (CSV만 처리)
                        continue
                    
                    self.dataframes[file_key] = df
                    
                except Exception as e:
                    st.warning(f"파일 로드 실패: {csv_file} - {str(e)}")
                    continue
            
            # 통합 데이터프레임 생성 (주요 분석용)
            self._create_unified_dataframe()
            
        except Exception as e:
            st.error(f"데이터 로드 중 오류 발생: {str(e)}")
    
    def _preprocess_inventory_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """국가 온실가스 인벤토리 데이터 전처리 (test.ipynb 방식)"""
        try:
            # 데이터 전치(transpose)
            df = df.set_index('분야 및 연도').T
            
            # 인덱스를 연도로 설정
            df.index.name = '연도'
            df = df.reset_index()
            
            # 연도 컬럼을 숫자로 변환
            df['연도'] = pd.to_numeric(df['연도'], errors='coerce')
            
            # 데이터 타입을 숫자로 변환
            for col in df.columns[1:]:  # 첫 번째 컬럼(연도) 제외
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            st.warning(f"인벤토리 데이터 전처리 실패: {str(e)}")
            return df
    
    def _create_unified_dataframe(self) -> None:
        """분석을 위한 통합 데이터프레임 생성 - 연도 기준으로 merge"""
        if not self.dataframes:
            return
        
        try:
            # 국가 온실가스 인벤토리 데이터를 기본으로 사용
            main_key = None
            for key in self.dataframes.keys():
                if "국가 온실가스 인벤토리" in key:
                    main_key = key
                    break
            
            if main_key:
                self.unified_df = self.dataframes[main_key].copy()
                
                # 다른 데이터프레임들과 연도 기준으로 merge
                for key, df in self.dataframes.items():
                    if key != main_key and '연도' in df.columns:
                        # 연도 컬럼이 있는 경우 merge
                        try:
                            # 중복 컬럼명 처리
                            df_to_merge = df.copy()
                            overlap_cols = set(self.unified_df.columns) & set(df_to_merge.columns)
                            overlap_cols.discard('연도')  # 연도 컬럼은 제외
                            
                            for col in overlap_cols:
                                df_to_merge = df_to_merge.rename(columns={col: f"{col}_{key}"})
                            
                            self.unified_df = pd.merge(
                                self.unified_df, 
                                df_to_merge, 
                                on='연도', 
                                how='outer'
                            )
                        except Exception as e:
                            st.warning(f"데이터 merge 실패: {key} - {str(e)}")
                            continue
                
                self.main_df = self.unified_df
            else:
                # 첫 번째 데이터프레임을 메인으로 사용
                self.main_df = list(self.dataframes.values())[0]
                
        except Exception as e:
            st.warning(f"통합 데이터프레임 생성 실패: {str(e)}")
            # 폴백: 첫 번째 데이터프레임 사용
            if self.dataframes:
                self.main_df = list(self.dataframes.values())[0]
    
    def create_visualization(self, query: str, data_subset: pd.DataFrame = None) -> Optional[str]:
        """
        데이터 시각화 생성
        
        Args:
            query: 사용자 질문
            data_subset: 시각화할 데이터 (None이면 전체 데이터 사용)
            
        Returns:
            base64 인코딩된 이미지 문자열 또는 None
        """
        try:
            if data_subset is None:
                data_subset = self.main_df
            
            # 그래프 타입 결정
            if any(word in query.lower() for word in ['추이', '변화', '트렌드', '시간']):
                return self._create_line_chart(data_subset, query)
            elif any(word in query.lower() for word in ['비교', '차이', '대비']):
                return self._create_bar_chart(data_subset, query)
            elif any(word in query.lower() for word in ['분포', '비율']):
                return self._create_pie_chart(data_subset, query)
            else:
                # 기본적으로 선 그래프 생성
                return self._create_line_chart(data_subset, query)
                
        except Exception as e:
            st.warning(f"시각화 생성 실패: {str(e)}")
            return None
    
    def _create_line_chart(self, df: pd.DataFrame, query: str) -> Optional[str]:
        """선 그래프 생성"""
        try:
            plt.figure(figsize=(12, 8))
            
            if '연도' in df.columns:
                # 연도별 총배출량 추이
                if '총배출량' in df.columns:
                    plt.plot(df['연도'], df['총배출량'], marker='o', linewidth=2, markersize=8)
                    plt.title('연도별 총배출량 변화 추이', fontsize=16, fontweight='bold')
                    plt.ylabel('총배출량 (백만톤 CO2eq)', fontsize=12)
                else:
                    # 숫자형 컬럼들 중 첫 번째 사용
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 1:  # 연도 제외
                        col_to_plot = [col for col in numeric_cols if col != '연도'][0]
                        plt.plot(df['연도'], df[col_to_plot], marker='o', linewidth=2, markersize=8)
                        plt.title(f'연도별 {col_to_plot} 변화 추이', fontsize=16, fontweight='bold')
                        plt.ylabel(col_to_plot, fontsize=12)
                
                plt.xlabel('연도', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 이미지를 base64로 인코딩
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            st.warning(f"선 그래프 생성 실패: {str(e)}")
            plt.close()
            return None
    
    def _create_bar_chart(self, df: pd.DataFrame, query: str) -> Optional[str]:
        """막대 그래프 생성 - 질문 내용을 분석하여 적절한 그래프 생성"""
        try:
            plt.figure(figsize=(12, 8))
            
            if '연도' not in df.columns:
                return None
            
            # 질문에서 연도 추출
            import re
            years_mentioned = re.findall(r'\b(19|20)\d{2}\b', query)
            years_mentioned = [int(year) for year in years_mentioned]
            
            # 총배출량 관련 컬럼 찾기
            total_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                         for keyword in ['총', 'total', '합계', '전체'])]
            
            if len(years_mentioned) >= 2 and total_cols:
                # 연도별 총배출량 비교
                years_data = []
                years_labels = []
                
                for year in sorted(years_mentioned):
                    year_data = df[df['연도'] == year]
                    if not year_data.empty and total_cols:
                        # 총배출량 컬럼 찾기
                        total_col = total_cols[0]  # 첫 번째 총배출량 컬럼 사용
                        value = year_data[total_col].iloc[0]
                        if not pd.isna(value):
                            years_data.append(value)
                            years_labels.append(f'{year}년')
                
                if years_data:
                    colors = ['#74b9ff', '#fd79a8', '#00b894', '#fdcb6e', '#e17055']
                    plt.bar(years_labels, years_data, color=colors[:len(years_data)])
                    plt.title('연도별 총배출량 비교', fontsize=16, fontweight='bold')
                    plt.ylabel('총배출량 (Gg CO2eq)', fontsize=12)
                    
                    # 값 표시
                    for i, v in enumerate(years_data):
                        plt.text(i, v + max(years_data) * 0.01, f'{v:,.0f}', 
                                ha='center', va='bottom', fontsize=11, fontweight='bold')
                else:
                    # 기본 막대 그래프 - 최신 연도 분야별 데이터
                    latest_year = df['연도'].max()
                    latest_data = df[df['연도'] == latest_year]
                    
                    numeric_cols = latest_data.select_dtypes(include=[np.number]).columns
                    numeric_cols = [col for col in numeric_cols if col != '연도'][:5]
                    
                    values = [latest_data[col].iloc[0] for col in numeric_cols if not pd.isna(latest_data[col].iloc[0])]
                    labels = [col for col in numeric_cols if not pd.isna(latest_data[col].iloc[0])]
                    
                    plt.bar(labels, values, color=plt.cm.Set3(np.linspace(0, 1, len(labels))))
                    plt.title(f'{latest_year}년 주요 지표 비교', fontsize=16, fontweight='bold')
                    plt.ylabel('값', fontsize=12)
                    plt.xticks(rotation=45, ha='right')
            
            elif years_mentioned and len(years_mentioned) == 1:
                # 단일 연도의 분야별 데이터
                year = years_mentioned[0]
                year_data = df[df['연도'] == year]
                
                if not year_data.empty:
                    numeric_cols = year_data.select_dtypes(include=[np.number]).columns
                    numeric_cols = [col for col in numeric_cols if col != '연도'][:5]
                    
                    values = [year_data[col].iloc[0] for col in numeric_cols if not pd.isna(year_data[col].iloc[0])]
                    labels = [col for col in numeric_cols if not pd.isna(year_data[col].iloc[0])]
                    
                    plt.bar(labels, values, color=plt.cm.Set3(np.linspace(0, 1, len(labels))))
                    plt.title(f'{year}년 분야별 배출량', fontsize=16, fontweight='bold')
                    plt.ylabel('배출량 (Gg CO2eq)', fontsize=12)
                    plt.xticks(rotation=45, ha='right')
            else:
                # 기본 막대 그래프 (최신 연도)
                latest_year = df['연도'].max()
                latest_data = df[df['연도'] == latest_year]
                
                numeric_cols = latest_data.select_dtypes(include=[np.number]).columns
                numeric_cols = [col for col in numeric_cols if col != '연도'][:5]
                
                values = [latest_data[col].iloc[0] for col in numeric_cols if not pd.isna(latest_data[col].iloc[0])]
                labels = [col for col in numeric_cols if not pd.isna(latest_data[col].iloc[0])]
                
                plt.bar(labels, values, color=plt.cm.Set3(np.linspace(0, 1, len(labels))))
                plt.title(f'{latest_year}년 주요 지표 비교', fontsize=16, fontweight='bold')
                plt.ylabel('값', fontsize=12)
                plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # 이미지를 base64로 인코딩
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            st.warning(f"막대 그래프 생성 실패: {str(e)}")
            plt.close()
            return None
    
    def _create_pie_chart(self, df: pd.DataFrame, query: str) -> Optional[str]:
        """파이 차트 생성"""
        try:
            plt.figure(figsize=(8, 8))
            
            # 최근 연도 데이터 사용
            if '연도' in df.columns:
                latest_year = df['연도'].max()
                latest_data = df[df['연도'] == latest_year]
                
                # 숫자형 컬럼들 선택 (상위 5개)
                numeric_cols = latest_data.select_dtypes(include=[np.number]).columns
                numeric_cols = [col for col in numeric_cols if col != '연도'][:5]
                
                values = [latest_data[col].iloc[0] for col in numeric_cols if not pd.isna(latest_data[col].iloc[0]) and latest_data[col].iloc[0] > 0]
                labels = [col for col in numeric_cols if not pd.isna(latest_data[col].iloc[0]) and latest_data[col].iloc[0] > 0]
                
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.title(f'{latest_year}년 분야별 비율', fontsize=16, fontweight='bold')
            
            plt.axis('equal')
            
            # 이미지를 base64로 인코딩
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            st.warning(f"파이 차트 생성 실패: {str(e)}")
            plt.close()
            return None
    
    def _setup_agent(self) -> None:
        """LangChain 에이전트 설정"""
        try:
            if not hasattr(self, 'main_df') or self.main_df is None:
                st.error("분석할 데이터가 없습니다.")
                return
            
            # ChatUpstage 모델 초기화
            llm = ChatUpstage(
                model="solar-mini-250422",
                temperature=0
            )
            
            # Pandas DataFrame Agent 생성
            self.agent = create_pandas_dataframe_agent(
                llm=llm,
                df=self.main_df,
                verbose=False,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                allow_dangerous_code=True,
                handle_parsing_errors=True
            )
            
        except Exception as e:
            st.error(f"에이전트 설정 중 오류 발생: {str(e)}")
    
    def ask(self, query: str) -> tuple:
        """
        사용자 질문에 대한 답변 생성
        
        Args:
            query: 사용자 질문
            
        Returns:
            (답변 문자열, 시각화 이미지 base64) 튜플
        """
        if not self.agent:
            return "에이전트가 초기화되지 않았습니다. 데이터를 확인해주세요.", None
        
        try:
            # 일반적인 invoke 방식 사용
            response = self.agent.invoke({"input": query})
            
            # 응답에서 output 추출
            if isinstance(response, dict) and 'output' in response:
                text_response = response['output']
            elif hasattr(response, 'content'):
                text_response = response.content
            else:
                text_response = str(response)
            
            # 그래프 요청인지 확인
            graph_keywords = ['그래프', '차트', '시각화', '그려', '보여줘', '플롯']
            if any(keyword in query for keyword in graph_keywords):
                visualization = self.create_visualization(query)
                return text_response, visualization
            
            return text_response, None
            
        except Exception as e:
            error_msg = str(e)
            
            # 파싱 오류에서 실제 답변 추출
            if "Final Answer:" in error_msg:
                try:
                    # Final Answer 부분 추출
                    answer_start = error_msg.find("Final Answer:") + len("Final Answer:")
                    answer_end = error_msg.find("\nFor troubleshooting")
                    if answer_end == -1:
                        answer_end = answer_start + 200  # 적당한 길이로 제한
                    
                    extracted_answer = error_msg[answer_start:answer_end].strip()
                    
                    # 그래프 요청인지 확인
                    graph_keywords = ['그래프', '차트', '시각화', '그려', '보여줘', '플롯']
                    if any(keyword in query for keyword in graph_keywords):
                        visualization = self.create_visualization(query)
                        return extracted_answer, visualization
                    
                    return extracted_answer, None
                except:
                    pass
            
            return f"질문 처리 중 오류가 발생했습니다: {error_msg[:200]}...", None
    
    def get_data_summary(self) -> Dict[str, Any]:
        """로드된 데이터의 요약 정보 반환"""
        summary = {
            "total_files": len(self.dataframes),
            "files": list(self.dataframes.keys()),
            "main_data_shape": self.main_df.shape if hasattr(self, 'main_df') else None,
            "main_data_columns": [str(col) for col in self.main_df.columns.tolist()] if hasattr(self, 'main_df') else []
        }
        return summary
    
    def get_available_data_info(self) -> str:
        """사용 가능한 데이터 정보를 문자열로 반환"""
        if not self.dataframes:
            return "로드된 데이터가 없습니다."
        
        info_lines = ["📊 **사용 가능한 데이터셋:**"]
        
        for key, df in self.dataframes.items():
            info_lines.append(f"- **{key}**: {df.shape[0]}행 × {df.shape[1]}열")
            
            # 주요 컬럼 정보 (처음 5개만) - 모든 컬럼명을 문자열로 변환
            main_cols = [str(col) for col in df.columns.tolist()[:5]]
            if len(df.columns) > 5:
                main_cols.append("...")
            info_lines.append(f"  - 주요 컬럼: {', '.join(main_cols)}")
        
        return "\n".join(info_lines)

# 전역 에이전트 인스턴스 (싱글톤 패턴)
_agent_instance = None

def get_carbon_agent() -> CarbonDataRAGAgent:
    """탄소 데이터 RAG 에이전트 인스턴스 반환 (싱글톤)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CarbonDataRAGAgent()
    return _agent_instance

def initialize_agent() -> CarbonDataRAGAgent:
    """에이전트 강제 재초기화"""
    global _agent_instance
    _agent_instance = CarbonDataRAGAgent()
    return _agent_instance

# 테스트 함수
if __name__ == "__main__":
    # 테스트 실행
    agent = CarbonDataRAGAgent()
    
    print("=== 데이터 요약 ===")
    summary = agent.get_data_summary()
    print(f"로드된 파일 수: {summary['total_files']}")
    print(f"파일 목록: {summary['files']}")
    
    if summary['main_data_shape']:
        print(f"메인 데이터 크기: {summary['main_data_shape']}")
        print(f"메인 데이터 컬럼: {summary['main_data_columns'][:5]}...")
    
    print("\n=== 테스트 질문 ===")
    test_queries = [
        "데이터에 몇 개의 행이 있어?",
        "총배출량의 평균은 얼마야?",
        "2017년의 총배출량은?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        answer, visualization = agent.ask(query)
        print(f"답변: {answer}")
        
        if visualization:
            st.image(f"data:image/png;base64,{visualization}") 