"""
메타데이터 관리 시스템
각 데이터셋의 설명, 컬럼 의미, 단위 등 메타정보 저장
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from datetime import datetime

@dataclass
class ColumnMetadata:
    """컬럼 메타데이터"""
    name: str
    description: str
    data_type: str
    unit: Optional[str] = None
    category: Optional[str] = None
    is_key: bool = False
    is_numeric: bool = False
    possible_values: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

@dataclass
class DatasetMetadata:
    """데이터셋 메타데이터"""
    name: str
    description: str
    source: str
    last_updated: str
    file_path: str
    file_hash: str
    shape: tuple
    columns: List[ColumnMetadata]
    relationships: Dict[str, List[str]]  # 다른 데이터셋과의 관계
    quality_score: float
    tags: List[str]

class MetadataManager:
    """데이터 메타정보 관리 클래스"""
    
    def __init__(self, metadata_file: str = "metadata.json"):
        """
        메타데이터 관리자 초기화
        
        Args:
            metadata_file: 메타데이터 저장 파일 경로
        """
        self.metadata_file = Path(metadata_file)
        self.metadata: Dict[str, DatasetMetadata] = {}
        self.column_mappings: Dict[str, Dict[str, str]] = {}
        
        # 기본 메타데이터 템플릿
        self.default_metadata = self._create_default_metadata()
        
        # 메타데이터 로드
        self.load_metadata()
    
    def _create_default_metadata(self) -> Dict[str, Dict]:
        """기본 메타데이터 템플릿 생성"""
        return {
            "3차_사전할당": {
                "description": "3차 계획기간 배출권 사전할당 데이터",
                "source": "한국거래소",
                "tags": ["배출권", "할당", "사전할당"],
                "key_columns": ["업체명", "업종"],
                "value_columns": ["할당량"],
                "unit": "tCO2eq"
            },
            "추가할당량": {
                "description": "배출권 추가할당량 데이터",
                "source": "한국거래소",
                "tags": ["배출권", "할당", "추가할당"],
                "key_columns": ["업체명", "업종"],
                "value_columns": ["추가할당량"],
                "unit": "tCO2eq"
            },
            "상쇄배출권": {
                "description": "상쇄배출권 발행량 데이터",
                "source": "한국거래소",
                "tags": ["상쇄배출권", "발행량"],
                "key_columns": ["사업명", "사업유형"],
                "value_columns": ["발행량"],
                "unit": "tCO2eq"
            },
            "국가 온실가스 인벤토리": {
                "description": "국가 온실가스 인벤토리 배출량 데이터 (1990-2021)",
                "source": "환경부 온실가스종합정보센터",
                "tags": ["온실가스", "인벤토리", "국가통계"],
                "key_columns": ["분야", "세부분야"],
                "value_columns": ["1990", "1991", "1992", "2021"],
                "unit": "MtCO2eq"
            },
            "기업_규모_지역별": {
                "description": "기업 규모 및 지역별 온실가스 배출량 데이터",
                "source": "환경부",
                "tags": ["기업", "지역별", "배출량"],
                "key_columns": ["지역", "규모"],
                "value_columns": ["배출량"],
                "unit": "tCO2eq"
            },
            "배출권_거래데이터": {
                "description": "배출권 거래 관련 데이터",
                "source": "한국거래소",
                "tags": ["배출권", "거래", "시장"],
                "key_columns": ["거래일", "거래유형"],
                "value_columns": ["거래량", "거래금액"],
                "unit": "tCO2eq, 원"
            },
            "한국에너지공단": {
                "description": "산업부문 에너지사용 및 온실가스배출량 통계",
                "source": "한국에너지공단",
                "tags": ["산업", "에너지", "배출량"],
                "key_columns": ["업종", "연도"],
                "value_columns": ["에너지사용량", "배출량"],
                "unit": "TOE, tCO2eq"
            }
        }
    
    def analyze_and_create_metadata(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """데이터셋들을 분석하여 메타데이터 생성"""
        for name, df in datasets.items():
            if name not in self.metadata:
                metadata = self._analyze_dataset(name, df)
                self.metadata[name] = metadata
        
        # 데이터셋 간 관계 분석
        self._analyze_relationships()
        
        # 메타데이터 저장
        self.save_metadata()
    
    def _analyze_dataset(self, name: str, df: pd.DataFrame) -> DatasetMetadata:
        """개별 데이터셋 분석하여 메타데이터 생성"""
        # 파일 해시 계산
        file_hash = hashlib.md5(str(df.values.tobytes()).encode()).hexdigest()
        
        # 컬럼 메타데이터 생성
        columns_metadata = []
        for col in df.columns:
            col_meta = self._analyze_column(col, df[col])
            columns_metadata.append(col_meta)
        
        # 기본 메타데이터 가져오기
        default_info = self.default_metadata.get(name, {})
        
        # 품질 점수 계산
        quality_score = self._calculate_quality_score(df)
        
        return DatasetMetadata(
            name=name,
            description=default_info.get("description", f"{name} 데이터"),
            source=default_info.get("source", "알 수 없음"),
            last_updated=datetime.now().isoformat(),
            file_path=f"data/{name}.csv",
            file_hash=file_hash,
            shape=df.shape,
            columns=columns_metadata,
            relationships={},
            quality_score=quality_score,
            tags=default_info.get("tags", ["온실가스"])
        )
    
    def _analyze_column(self, col_name: str, series: pd.Series) -> ColumnMetadata:
        """개별 컬럼 분석"""
        # 데이터 타입 결정
        dtype = str(series.dtype)
        is_numeric = pd.api.types.is_numeric_dtype(series)
        
        # 카테고리 결정
        category = self._determine_column_category(col_name)
        
        # 설명 생성
        description = self._generate_column_description(col_name, category)
        
        # 단위 결정
        unit = self._determine_unit(col_name, category)
        
        # 가능한 값들 (카테고리형인 경우)
        possible_values = None
        if not is_numeric and series.nunique() < 50:
            possible_values = series.unique().tolist()[:20]  # 최대 20개
        
        # 최솟값, 최댓값 (숫자형인 경우)
        min_value = None
        max_value = None
        if is_numeric:
            min_value = float(series.min()) if not series.isna().all() else None
            max_value = float(series.max()) if not series.isna().all() else None
        
        return ColumnMetadata(
            name=col_name,
            description=description,
            data_type=dtype,
            unit=unit,
            category=category,
            is_key=self._is_key_column(col_name),
            is_numeric=is_numeric,
            possible_values=possible_values,
            min_value=min_value,
            max_value=max_value
        )
    
    def _determine_column_category(self, col_name: str) -> str:
        """컬럼 카테고리 결정"""
        col_lower = str(col_name).lower()
        
        if any(word in col_lower for word in ['년', 'year', '연도']):
            return "시간"
        elif any(word in col_lower for word in ['배출량', '배출', 'emission']):
            return "배출량"
        elif any(word in col_lower for word in ['할당량', '할당', 'allocation']):
            return "할당량"
        elif any(word in col_lower for word in ['거래량', '거래', 'trade']):
            return "거래량"
        elif any(word in col_lower for word in ['업체', '기업', '회사', 'company']):
            return "기업정보"
        elif any(word in col_lower for word in ['업종', '산업', 'industry']):
            return "산업분류"
        elif any(word in col_lower for word in ['지역', '시도', 'region']):
            return "지역정보"
        elif any(word in col_lower for word in ['분야', '부문', 'sector']):
            return "분야분류"
        else:
            return "기타"
    
    def _generate_column_description(self, col_name: str, category: str) -> str:
        """컬럼 설명 생성"""
        descriptions = {
            "시간": f"{col_name} (연도 정보)",
            "배출량": f"{col_name} (온실가스 배출량)",
            "할당량": f"{col_name} (배출권 할당량)",
            "거래량": f"{col_name} (배출권 거래량)",
            "기업정보": f"{col_name} (기업/업체 정보)",
            "산업분류": f"{col_name} (산업/업종 분류)",
            "지역정보": f"{col_name} (지역 정보)",
            "분야분류": f"{col_name} (분야/부문 분류)",
            "기타": f"{col_name}"
        }
        return descriptions.get(category, col_name)
    
    def _determine_unit(self, col_name: str, category: str) -> Optional[str]:
        """컬럼 단위 결정"""
        col_lower = str(col_name).lower()
        
        if category in ["배출량", "할당량", "거래량"]:
            if any(word in col_lower for word in ['mt', '백만톤', 'million']):
                return "MtCO2eq"
            else:
                return "tCO2eq"
        elif category == "시간":
            return "년"
        elif "금액" in col_lower or "가격" in col_lower:
            return "원"
        else:
            return None
    
    def _is_key_column(self, col_name: str) -> bool:
        """키 컬럼 여부 판단"""
        key_indicators = ['id', '코드', '업체명', '기업명', '사업명', '년', '연도']
        col_lower = str(col_name).lower()
        return any(indicator in col_lower for indicator in key_indicators)
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """데이터 품질 점수 계산 (0-1)"""
        score = 0.0
        
        # 완성도 (결측값 비율)
        completeness = 1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))
        score += completeness * 0.4
        
        # 일관성 (데이터 타입 일관성)
        consistency = 0.8  # 기본값 (실제로는 더 복잡한 로직 필요)
        score += consistency * 0.3
        
        # 유효성 (합리적인 값 범위)
        validity = 0.9  # 기본값
        score += validity * 0.3
        
        return min(score, 1.0)
    
    def _analyze_relationships(self) -> None:
        """데이터셋 간 관계 분석"""
        dataset_names = list(self.metadata.keys())
        
        for name1 in dataset_names:
            relationships = {}
            
            for name2 in dataset_names:
                if name1 != name2:
                    # 공통 컬럼 찾기
                    common_columns = self._find_common_columns(name1, name2)
                    if common_columns:
                        relationships[name2] = common_columns
            
            self.metadata[name1].relationships = relationships
    
    def _find_common_columns(self, dataset1: str, dataset2: str) -> List[str]:
        """두 데이터셋 간 공통 컬럼 찾기"""
        if dataset1 not in self.metadata or dataset2 not in self.metadata:
            return []
        
        cols1 = {str(col.name).lower() for col in self.metadata[dataset1].columns}
        cols2 = {str(col.name).lower() for col in self.metadata[dataset2].columns}
        
        common = cols1.intersection(cols2)
        return list(common)
    
    def get_dataset_info(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """데이터셋 정보 조회"""
        if dataset_name in self.metadata:
            return asdict(self.metadata[dataset_name])
        return None
    
    def get_column_info(self, dataset_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """컬럼 정보 조회"""
        if dataset_name in self.metadata:
            for col in self.metadata[dataset_name].columns:
                if col.name == column_name:
                    return asdict(col)
        return None
    
    def search_datasets_by_tag(self, tag: str) -> List[str]:
        """태그로 데이터셋 검색"""
        matching_datasets = []
        for name, metadata in self.metadata.items():
            if tag.lower() in [t.lower() for t in metadata.tags]:
                matching_datasets.append(name)
        return matching_datasets
    
    def search_columns_by_category(self, category: str) -> Dict[str, List[str]]:
        """카테고리로 컬럼 검색"""
        matching_columns = {}
        for dataset_name, metadata in self.metadata.items():
            cols = [col.name for col in metadata.columns if col.category == category]
            if cols:
                matching_columns[dataset_name] = cols
        return matching_columns
    
    def get_data_lineage(self, dataset_name: str) -> Dict[str, Any]:
        """데이터 계보 정보 조회"""
        if dataset_name not in self.metadata:
            return {}
        
        metadata = self.metadata[dataset_name]
        return {
            "dataset": dataset_name,
            "source": metadata.source,
            "last_updated": metadata.last_updated,
            "relationships": metadata.relationships,
            "quality_score": metadata.quality_score
        }
    
    def save_metadata(self) -> None:
        """메타데이터를 파일에 저장"""
        metadata_dict = {}
        for name, metadata in self.metadata.items():
            metadata_dict[name] = asdict(metadata)
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, ensure_ascii=False, indent=2)
    
    def load_metadata(self) -> None:
        """파일에서 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                
                for name, data in metadata_dict.items():
                    # ColumnMetadata 객체들 복원
                    columns = [ColumnMetadata(**col_data) for col_data in data['columns']]
                    data['columns'] = columns
                    
                    # DatasetMetadata 객체 생성
                    self.metadata[name] = DatasetMetadata(**data)
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"메타데이터 로드 실패: {e}")
                self.metadata = {}
    
    def generate_data_catalog(self) -> str:
        """데이터 카탈로그 생성"""
        catalog = "# 데이터 카탈로그\n\n"
        
        for name, metadata in self.metadata.items():
            catalog += f"## {name}\n"
            catalog += f"**설명**: {metadata.description}\n"
            catalog += f"**출처**: {metadata.source}\n"
            catalog += f"**크기**: {metadata.shape[0]}행 × {metadata.shape[1]}열\n"
            catalog += f"**품질점수**: {metadata.quality_score:.2f}\n"
            catalog += f"**태그**: {', '.join(metadata.tags)}\n\n"
            
            catalog += "### 컬럼 정보\n"
            for col in metadata.columns:
                catalog += f"- **{col.name}** ({col.category}): {col.description}"
                if col.unit:
                    catalog += f" [{col.unit}]"
                catalog += "\n"
            
            if metadata.relationships:
                catalog += "\n### 관련 데이터셋\n"
                for related, common_cols in metadata.relationships.items():
                    catalog += f"- {related}: 공통 컬럼 {', '.join(common_cols)}\n"
            
            catalog += "\n---\n\n"
        
        return catalog 