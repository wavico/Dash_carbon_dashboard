"""
통합 데이터 전처리 시스템
모든 CSV 파일을 분석하고 표준화된 형태로 변환
"""

import pandas as pd
import numpy as np
import os
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

@dataclass
class DatasetInfo:
    """데이터셋 정보를 저장하는 클래스"""
    filename: str
    shape: Tuple[int, int]
    columns: List[str]
    data_types: Dict[str, str]
    has_year_columns: bool
    year_columns: List[str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    missing_values: Dict[str, int]
    description: str

class DataPreprocessor:
    """모든 CSV 통합 및 전처리 클래스"""
    
    def __init__(self, data_folder: str):
        """
        데이터 전처리기 초기화
        
        Args:
            data_folder: 데이터 폴더 경로
        """
        self.data_folder = Path(data_folder)
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.dataset_info: Dict[str, DatasetInfo] = {}
        self.unified_data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def analyze_all_datasets(self) -> Dict[str, DatasetInfo]:
        """모든 CSV 파일을 분석하여 스키마 정보 추출"""
        csv_files = list(self.data_folder.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                # 다양한 인코딩으로 시도
                df = self._load_csv_with_encoding(csv_file)
                if df is not None:
                    info = self._analyze_dataset(df, csv_file.name)
                    self.datasets[csv_file.stem] = df
                    self.dataset_info[csv_file.stem] = info
                    self.logger.info(f"분석 완료: {csv_file.name}")
                    
            except Exception as e:
                self.logger.error(f"파일 분석 실패 {csv_file.name}: {e}")
                
        return self.dataset_info
    
    def _load_csv_with_encoding(self, filepath: Path) -> Optional[pd.DataFrame]:
        """다양한 인코딩으로 CSV 파일 로드 시도"""
        encodings = ['utf-8', 'euc-kr', 'cp949', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                
                # 국가 온실가스 인벤토리 파일의 경우 특별 처리
                if '국가 온실가스 인벤토리' in filepath.name:
                    print(f"📊 국가 온실가스 인벤토리 데이터 로드: {filepath.name}")
                    print(f"   - 원본 shape: {df.shape}")
                    print(f"   - 첫 번째 컬럼: {df.columns[0]}")
                    print(f"   - 두 번째 컬럼: {df.columns[1] if len(df.columns) > 1 else 'N/A'}")
                    
                    # 2017년과 2021년 데이터 확인
                    if len(df.columns) > 1:
                        row_2017 = df[df.iloc[:, 0] == 2017]
                        row_2021 = df[df.iloc[:, 0] == 2021]
                        if not row_2017.empty:
                            print(f"   - 2017년 총배출량: {row_2017.iloc[0, 1]} (백만톤 CO₂)")
                        if not row_2021.empty:
                            print(f"   - 2021년 총배출량: {row_2021.iloc[0, 1]} (백만톤 CO₂)")
                    
                    # 데이터가 이미 올바른 형태인지 확인 (연도가 첫 번째 컬럼에 있는 경우)
                    if df.iloc[:, 0].dtype in ['int64', 'float64'] or any(str(val).isdigit() and 1990 <= int(str(val)) <= 2030 for val in df.iloc[:, 0].dropna() if str(val).replace('.', '').isdigit()):
                        print("   - 데이터가 이미 올바른 형태 (연도가 첫 번째 컬럼)")
                        # 컬럼명 정리
                        if len(df.columns) > 1:
                            df.columns = ['연도', '총배출량'] + list(df.columns[2:])
                        return df
                    
                    # 전치가 필요한 경우에만 수행
                    elif df.shape[0] < df.shape[1]:  # 행보다 열이 더 많으면 전치
                        print("   - 전치(transpose) 수행")
                        df = df.set_index(df.columns[0]).T
                        df.index.name = '연도'
                        df = df.reset_index()
                        print(f"   - 전치 후 shape: {df.shape}")
                
                return df
                
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
                
        return None
    
    def _analyze_dataset(self, df: pd.DataFrame, filename: str) -> DatasetInfo:
        """개별 데이터셋 분석"""
        # 연도 컬럼 찾기
        year_pattern = r'(\d{4})'
        year_columns = []
        
        for col in df.columns:
            if re.search(year_pattern, str(col)):
                year_columns.append(col)
        
        # 숫자형 컬럼 찾기
        numeric_columns = []
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                numeric_columns.append(col)
            else:
                # 문자열이지만 숫자로 변환 가능한 컬럼 찾기
                try:
                    pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                    if not df[col].isna().all():
                        numeric_columns.append(col)
                except:
                    pass
        
        # 카테고리형 컬럼 찾기
        categorical_columns = [col for col in df.columns if col not in numeric_columns]
        
        # 결측값 계산
        missing_values = df.isnull().sum().to_dict()
        
        # 데이터 타입 정보
        data_types = {col: str(df[col].dtype) for col in df.columns}
        
        # 파일별 설명 생성
        description = self._generate_description(filename, df)
        
        return DatasetInfo(
            filename=filename,
            shape=df.shape,
            columns=list(df.columns),
            data_types=data_types,
            has_year_columns=len(year_columns) > 0,
            year_columns=year_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            missing_values=missing_values,
            description=description
        )
    
    def _generate_description(self, filename: str, df: pd.DataFrame) -> str:
        """파일명과 데이터를 기반으로 설명 생성"""
        descriptions = {
            '3차_사전할당': '3차 계획기간 배출권 사전할당 데이터',
            '추가할당량': '배출권 추가할당량 데이터',
            '상쇄배출권': '상쇄배출권 발행량 데이터',
            'CLM_온실가스': '온실가스 배출량 관련 데이터',
            '국가 온실가스 인벤토리': '국가 온실가스 인벤토리 배출량 데이터 (1990-2021)',
            '기업_규모_지역별': '기업 규모 및 지역별 온실가스 배출량 데이터',
            '배출권_거래데이터': '배출권 거래 관련 데이터',
            '배출권총수량': '배출권 총수량 데이터',
            '한국에너지공단': '산업부문 에너지사용 및 온실가스배출량 통계',
            '환경부': '환경부 온실가스종합정보센터 국가 온실가스 인벤토리 배출량'
        }
        
        for key, desc in descriptions.items():
            if key in filename:
                return desc
                
        return f"온실가스 관련 데이터 ({filename})"
    
    def standardize_data(self) -> pd.DataFrame:
        """모든 데이터를 표준화된 형태로 통합"""
        unified_rows = []
        
        for dataset_name, df in self.datasets.items():
            info = self.dataset_info[dataset_name]
            
            # 연도별 데이터가 있는 경우 시계열 형태로 변환
            if info.has_year_columns:
                standardized = self._convert_to_timeseries(df, dataset_name, info)
                unified_rows.extend(standardized)
            else:
                # 연도 정보가 없는 경우 메타데이터로 처리
                self.metadata[dataset_name] = df.to_dict('records')
        
        # 통합 데이터프레임 생성
        if unified_rows:
            self.unified_data = pd.DataFrame(unified_rows)
            self.unified_data = self._clean_unified_data(self.unified_data)
            
        return self.unified_data
    
    def _convert_to_timeseries(self, df: pd.DataFrame, dataset_name: str, info: DatasetInfo) -> List[Dict]:
        """데이터를 시계열 형태로 변환"""
        rows = []
        
        # 연도 컬럼들을 찾아서 시계열 데이터로 변환
        year_columns = info.year_columns
        non_year_columns = [col for col in df.columns if col not in year_columns]
        
        for _, row in df.iterrows():
            # 각 연도별로 레코드 생성
            for year_col in year_columns:
                year = self._extract_year(year_col)
                if year:
                    record = {
                        'dataset': dataset_name,
                        'year': year,
                        'value': self._clean_numeric_value(row[year_col]),
                    }
                    
                    # 비연도 컬럼들을 메타데이터로 추가
                    for col in non_year_columns:
                        record[f'meta_{col}'] = row[col]
                    
                    rows.append(record)
        
        return rows
    
    def _extract_year(self, year_string: str) -> Optional[int]:
        """문자열에서 연도 추출"""
        match = re.search(r'(\d{4})', str(year_string))
        if match:
            year = int(match.group(1))
            if 1990 <= year <= 2030:  # 합리적인 연도 범위
                return year
        return None
    
    def _clean_numeric_value(self, value: Any) -> Optional[float]:
        """숫자 값 정리"""
        if pd.isna(value):
            return None
            
        if isinstance(value, (int, float)):
            return float(value)
            
        # 문자열인 경우 숫자로 변환 시도
        try:
            # 쉼표 제거 후 숫자 변환
            cleaned = str(value).replace(',', '').replace(' ', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _clean_unified_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """통합 데이터 정리"""
        # 결측값 처리
        df = df.dropna(subset=['value'])
        
        # 데이터 타입 최적화
        df['year'] = df['year'].astype(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # 이상치 탐지 및 처리 (IQR 방법)
        Q1 = df['value'].quantile(0.25)
        Q3 = df['value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 이상치 플래그 추가
        df['is_outlier'] = (df['value'] < lower_bound) | (df['value'] > upper_bound)
        
        # 정렬
        df = df.sort_values(['dataset', 'year']).reset_index(drop=True)
        
        return df
    
    def get_data_summary(self) -> Dict[str, Any]:
        """데이터 요약 정보 반환"""
        summary = {
            'total_datasets': len(self.datasets),
            'datasets_info': {},
            'unified_data_shape': self.unified_data.shape if self.unified_data is not None else None,
            'year_range': None,
            'total_records': 0
        }
        
        # 각 데이터셋 정보
        for name, info in self.dataset_info.items():
            summary['datasets_info'][name] = {
                'shape': info.shape,
                'columns_count': len(info.columns),
                'has_year_data': info.has_year_columns,
                'year_columns_count': len(info.year_columns),
                'description': info.description
            }
        
        # 통합 데이터 정보
        if self.unified_data is not None:
            summary['year_range'] = (
                self.unified_data['year'].min(),
                self.unified_data['year'].max()
            )
            summary['total_records'] = len(self.unified_data)
            summary['datasets_in_unified'] = self.unified_data['dataset'].nunique()
        
        return summary
    
    def get_dataset_by_name(self, name: str) -> Optional[pd.DataFrame]:
        """이름으로 데이터셋 조회"""
        return self.datasets.get(name)
    
    def get_unified_data(self) -> Optional[pd.DataFrame]:
        """통합 데이터 반환"""
        return self.unified_data
    
    def filter_data(self, dataset: str = None, year_range: Tuple[int, int] = None, 
                   value_range: Tuple[float, float] = None) -> pd.DataFrame:
        """조건에 따른 데이터 필터링"""
        if self.unified_data is None:
            return pd.DataFrame()
        
        filtered = self.unified_data.copy()
        
        if dataset:
            filtered = filtered[filtered['dataset'] == dataset]
        
        if year_range:
            start_year, end_year = year_range
            filtered = filtered[
                (filtered['year'] >= start_year) & 
                (filtered['year'] <= end_year)
            ]
        
        if value_range:
            min_val, max_val = value_range
            filtered = filtered[
                (filtered['value'] >= min_val) & 
                (filtered['value'] <= max_val)
            ]
        
        return filtered 