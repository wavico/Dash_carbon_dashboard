"""
동적 시각화 엔진
질문 타입에 따른 최적 차트 자동 선택 및 생성
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import base64
from io import BytesIO
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
from matplotlib.ticker import FuncFormatter
from scipy import stats  # Z-score 계산용 추가

warnings.filterwarnings('ignore')

class VisualizationEngine:
    """동적 차트 생성 클래스"""
    
    def __init__(self):
        """시각화 엔진 초기화"""
        # 한글 폰트 설정
        self._setup_korean_font()
        
        # 색상 팔레트 설정
        self.color_palettes = {
            'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            'pastel': ['#AEC7E8', '#FFBB78', '#98DF8A', '#FF9896', '#C5B0D5', '#C49C94'],
            'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        }
        
        # 기본 스타일 설정
        plt.style.use('default')
        sns.set_palette("husl")
        
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            # matplotlib 폰트 캐시 클리어 (안전하게)
            try:
                import matplotlib.font_manager
                if hasattr(matplotlib.font_manager, '_rebuild'):
                    matplotlib.font_manager._rebuild()
            except:
                pass  # 폰트 캐시 클리어 실패해도 계속 진행
            
            # Windows 환경에서 직접 폰트 파일 경로 설정
            font_paths = [
                'C:/Windows/Fonts/malgun.ttf',     # 맑은 고딕
                'C:/Windows/Fonts/malgunbd.ttf',   # 맑은 고딕 볼드
                'C:/Windows/Fonts/gulim.ttc',      # 굴림
                'C:/Windows/Fonts/batang.ttc',     # 바탕
                'C:/Windows/Fonts/dotum.ttc'       # 돋움
            ]
            
            korean_font_found = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 폰트 등록
                        fm.fontManager.addfont(font_path)
                        font_prop = fm.FontProperties(fname=font_path)
                        font_name = font_prop.get_name()
                        
                        # matplotlib 설정
                        plt.rcParams['font.family'] = font_name
                        plt.rcParams['axes.unicode_minus'] = False
                        
                        # 한글 테스트
                        test_fig, test_ax = plt.subplots(figsize=(1, 1))
                        test_ax.text(0.5, 0.5, '한글테스트', fontsize=12)
                        plt.close(test_fig)
                        
                        korean_font_found = True
                        print(f"✅ 한글 폰트 설정 성공: {font_name} ({font_path})")
                        break
                        
                    except Exception as e:
                        print(f"폰트 설정 실패 ({font_path}): {e}")
                        continue
            
            if not korean_font_found:
                # 시스템 폰트 이름으로 시도
                korean_fonts = ['Malgun Gothic', 'NanumGothic', 'Gulim', 'Dotum', 'Batang']
                available_fonts = [f.name for f in fm.fontManager.ttflist]
                
                for font in korean_fonts:
                    if font in available_fonts:
                        plt.rcParams['font.family'] = font
                        plt.rcParams['axes.unicode_minus'] = False
                        korean_font_found = True
                        print(f"✅ 시스템 한글 폰트 설정: {font}")
                        break
                
                if not korean_font_found:
                    print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
                    plt.rcParams['font.family'] = 'DejaVu Sans'
                    plt.rcParams['axes.unicode_minus'] = False
                    
        except Exception as e:
            print(f"폰트 설정 중 오류: {e}")
            plt.rcParams['font.family'] = 'DejaVu Sans'
            plt.rcParams['axes.unicode_minus'] = False
    
    def _ensure_korean_font(self):
        """차트 생성 전 한글 폰트 재확인"""
        # 매번 폰트 설정 재적용
        try:
            if os.path.exists('C:/Windows/Fonts/malgun.ttf'):
                font_prop = fm.FontProperties(fname='C:/Windows/Fonts/malgun.ttf')
                plt.rcParams['font.family'] = font_prop.get_name()
            elif 'Malgun Gothic' in [f.name for f in fm.fontManager.ttflist]:
                plt.rcParams['font.family'] = 'Malgun Gothic'
            else:
                plt.rcParams['font.family'] = 'Gulim'
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
    
    def _format_value_smart(self, value: float) -> str:
        """값을 읽기 쉬운 형태로 포맷팅 (국가 온실가스 인벤토리 데이터는 이미 백만톤 단위)"""
        # 국가 온실가스 인벤토리 데이터는 이미 백만톤 CO₂ 단위이므로 추가 변환 없이 표시
        if abs(value) >= 1e6:
            return f"{value:,.0f} 백만톤 CO₂"  # 백만 이상은 그대로 표시
        elif abs(value) >= 1e3:
            return f"{value:,.0f} 백만톤 CO₂"  # 천 이상도 그대로 표시
        else:
            return f"{value:.1f} 백만톤 CO₂"
    
    def _get_smart_formatter(self, values: pd.Series) -> FuncFormatter:
        """데이터 범위에 따른 스마트 포맷터 생성 (국가 온실가스 인벤토리 데이터용)"""
        max_val = abs(values).max()
        
        # 국가 온실가스 인벤토리 데이터는 이미 백만톤 CO₂ 단위
        # 따라서 추가 변환 없이 단위만 표시
        if max_val >= 1e6:
            return FuncFormatter(lambda x, p: f"{x:,.0f}" if x != 0 else "0")
        elif max_val >= 1e3:
            return FuncFormatter(lambda x, p: f"{x:,.0f}" if x != 0 else "0")
        else:
            return FuncFormatter(lambda x, p: f"{x:.1f}" if x != 0 else "0")
    
    def _apply_smart_y_limits(self, ax, values: pd.Series):
        """데이터에 적합한 Y축 범위 설정"""
        if values.empty:
            return
        
        min_val = values.min()
        max_val = values.max()
        
        # 값의 범위 계산
        value_range = max_val - min_val
        
        # Y축 하한 설정 (0부터 시작하지 않도록)
        if min_val > 0:
            # 최솟값이 양수면 적절한 여백을 둔 하한 설정
            margin = value_range * 0.1
            y_min = max(0, min_val - margin)
        else:
            y_min = min_val - abs(min_val) * 0.1
        
        # Y축 상한 설정
        y_max = max_val + value_range * 0.1
        
        # 극단적인 차이가 있는 경우 로그 스케일 고려
        if max_val / abs(min_val) > 1000 and min_val > 0:
            print("📊 극단적인 값 차이로 인해 로그 스케일 적용")
            ax.set_yscale('log')
        else:
            ax.set_ylim(y_min, y_max)
        
        print(f"📊 Y축 범위 설정: {y_min:,.0f} ~ {y_max:,.0f}")
    
    def _detect_and_handle_outliers(self, data: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """이상값 탐지 및 처리 (더 적극적)"""
        if 'value' not in data.columns or data.empty:
            return data
        
        data_clean = data.copy()
        original_count = len(data_clean)
        
        if method == 'iqr':
            # IQR 방법 (더 엄격하게)
            q1 = data_clean['value'].quantile(0.25)
            q3 = data_clean['value'].quantile(0.75)
            iqr = q3 - q1
            
            # 이상값 범위 (더 엄격하게 설정)
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # 이상값 제거
            outliers_mask = (data_clean['value'] < lower_bound) | (data_clean['value'] > upper_bound)
            outliers_count = outliers_mask.sum()
            
            if outliers_count > 0 and outliers_count < original_count * 0.9:  # 90% 이상 제거하지 않음
                print(f"⚠️ IQR 이상값 {outliers_count}개 제거 (범위: {lower_bound:,.0f} ~ {upper_bound:,.0f})")
                data_clean = data_clean[~outliers_mask]
        
        elif method == 'percentile':
            # 백분위수 방법 (상위/하위 5% 제거)
            lower_bound = data_clean['value'].quantile(0.05)
            upper_bound = data_clean['value'].quantile(0.95)
            
            outliers_mask = (data_clean['value'] < lower_bound) | (data_clean['value'] > upper_bound)
            outliers_count = outliers_mask.sum()
            
            if outliers_count > 0:
                print(f"⚠️ 상하위 5% 이상값 {outliers_count}개 제거")
                data_clean = data_clean[~outliers_mask]
        
        elif method == 'zscore':
            # Z-score 방법 (|z| > 2.5인 값 제거)
            z_scores = np.abs(stats.zscore(data_clean['value']))
            outliers_mask = z_scores > 2.5
            outliers_count = outliers_mask.sum()
            
            if outliers_count > 0 and outliers_count < original_count * 0.9:
                print(f"⚠️ Z-score 이상값 {outliers_count}개 제거 (|z| > 2.5)")
                data_clean = data_clean[~outliers_mask]
        
        return data_clean
    
    def _determine_outlier_strategy(self, data: pd.DataFrame) -> str:
        """데이터 특성에 따른 이상값 처리 전략 결정 (더 적극적)"""
        if 'value' not in data.columns or data.empty:
            return 'none'
        
        values = data['value']
        
        # 기본 통계
        std_dev = values.std()
        mean_val = values.mean()
        cv = std_dev / mean_val if mean_val != 0 else float('inf')  # 변동계수
        
        # 범위 차이
        max_val = values.max()
        min_val = values.min()
        range_ratio = max_val / abs(min_val) if min_val != 0 else float('inf')
        
        # 중앙값과 평균의 차이
        median_val = values.median()
        median_mean_ratio = abs(median_val - mean_val) / mean_val if mean_val != 0 else 0
        
        print(f"📊 데이터 특성 분석: CV={cv:.2f}, 범위비율={range_ratio:.2f}, 중앙값-평균비율={median_mean_ratio:.2f}")
        
        # 전략 결정 (더 적극적으로)
        if cv > 5 or range_ratio > 100 or median_mean_ratio > 0.5:  # 매우 불균등한 데이터
            return 'percentile'
        elif cv > 2 or range_ratio > 10:   # 불균등한 데이터
            return 'iqr'
        elif cv > 1:  # 약간 불균등한 데이터
            return 'zscore'
        else:
            return 'none'
    
    def create_visualization(self, data: pd.DataFrame, chart_type: str, 
                           title: str, params: Dict[str, Any]) -> Optional[str]:
        """
        데이터와 매개변수를 바탕으로 시각화 생성
        
        Args:
            data: 시각화할 데이터
            chart_type: 차트 타입 ('line', 'bar', 'pie', 'scatter' 등)
            title: 차트 제목
            params: 시각화 매개변수
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        if data.empty:
            return None
        
        try:
            # 차트 타입에 따른 시각화 생성
            if chart_type == 'line':
                return self._create_line_chart(data, title, params)
            elif chart_type == 'bar':
                return self._create_bar_chart(data, title, params)
            elif chart_type == 'pie':
                return self._create_pie_chart(data, title, params)
            elif chart_type == 'scatter':
                return self._create_scatter_plot(data, title, params)
            elif chart_type == 'heatmap':
                return self._create_heatmap(data, title, params)
            elif chart_type == 'histogram':
                return self._create_histogram(data, title, params)
            elif chart_type == 'box':
                return self._create_box_plot(data, title, params)
            elif chart_type == 'area':
                return self._create_area_chart(data, title, params)
            else:
                return self._create_bar_chart(data, title, params)  # 기본값
                
        except Exception as e:
            print(f"시각화 생성 오류: {e}")
            return None
    
    def _create_line_chart(self, data: pd.DataFrame, title: str, 
                          params: Dict[str, Any]) -> str:
        """선 그래프 생성"""
        self._ensure_korean_font()  # 한글 폰트 재설정
        
        # 이상값 처리 전략 결정
        outlier_strategy = self._determine_outlier_strategy(data)
        if outlier_strategy != 'none':
            data = self._detect_and_handle_outliers(data, outlier_strategy)
        
        if data.empty:
            print("⚠️ 이상값 제거 후 데이터가 비어있습니다.")
            return None
            
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 데이터 그룹화 및 집계
        if 'dataset' in data.columns:
            grouped = data.groupby(['year', 'dataset'])['value'].sum().reset_index()
            
            # 스마트 포맷터 적용
            all_values = grouped['value']
            formatter = self._get_smart_formatter(all_values)
            
            for dataset in grouped['dataset'].unique():
                dataset_data = grouped[grouped['dataset'] == dataset]
                ax.plot(dataset_data['year'], dataset_data['value'], 
                       marker='o', linewidth=2, label=dataset, markersize=6)
            
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Y축 범위 설정
            self._apply_smart_y_limits(ax, all_values)
            
        else:
            # 단일 시계열
            yearly_data = data.groupby('year')['value'].sum().reset_index()
            
            # 스마트 포맷터 적용
            formatter = self._get_smart_formatter(yearly_data['value'])
            
            ax.plot(yearly_data['year'], yearly_data['value'], 
                   marker='o', linewidth=3, markersize=8, color='#1f77b4')
            
            # Y축 범위 설정
            self._apply_smart_y_limits(ax, yearly_data['value'])
        
        # Y축 포맷터 적용
        ax.yaxis.set_major_formatter(formatter)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('배출량 (백만톤 CO₂)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_bar_chart(self, data: pd.DataFrame, title: str, 
                         params: Dict[str, Any]) -> str:
        """막대 그래프 생성"""
        self._ensure_korean_font()  # 한글 폰트 재설정
        
        # 이상값 처리 전략 결정
        outlier_strategy = self._determine_outlier_strategy(data)
        if outlier_strategy != 'none':
            data = self._detect_and_handle_outliers(data, outlier_strategy)
        
        if data.empty:
            print("⚠️ 이상값 제거 후 데이터가 비어있습니다.")
            return None
        
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 연도별 총합 계산 (비교 차트용)
        if 'year' in data.columns and len(data['year'].unique()) > 1:
            yearly_totals = data.groupby('year')['value'].sum().reset_index()
            
            # 스마트 포맷터 적용
            formatter = self._get_smart_formatter(yearly_totals['value'])
            
            bars = ax.bar(yearly_totals['year'].astype(str), yearly_totals['value'],
                         color=self.color_palettes['default'][:len(yearly_totals)],
                         alpha=0.8, edgecolor='black', linewidth=1)
            
            # 값 표시 (스마트 포맷팅)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       self._format_value_smart(height),
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_xlabel('연도', fontsize=12)
            
            # Y축 포맷터 적용
            ax.yaxis.set_major_formatter(formatter)
            
            # Y축 범위 설정
            self._apply_smart_y_limits(ax, yearly_totals['value'])
            
        elif 'dataset' in data.columns:
            # 데이터셋별 집계
            dataset_totals = data.groupby('dataset')['value'].sum().reset_index()
            dataset_totals = dataset_totals.sort_values('value', ascending=False)
            
            # 너무 많은 데이터셋이 있으면 상위 10개만
            if len(dataset_totals) > 10:
                dataset_totals = dataset_totals.head(10)
            
            # 스마트 포맷터 적용
            formatter = self._get_smart_formatter(dataset_totals['value'])
            
            bars = ax.bar(range(len(dataset_totals)), dataset_totals['value'],
                         color=self.color_palettes['default'][:len(dataset_totals)],
                         alpha=0.8, edgecolor='black', linewidth=1)
            
            ax.set_xticks(range(len(dataset_totals)))
            ax.set_xticklabels(dataset_totals['dataset'], rotation=45, ha='right')
            
            # 값 표시 (스마트 포맷팅)
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       self._format_value_smart(height),
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Y축 포맷터 적용
            ax.yaxis.set_major_formatter(formatter)
            
            # Y축 범위 설정
            self._apply_smart_y_limits(ax, dataset_totals['value'])
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('배출량', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_pie_chart(self, data: pd.DataFrame, title: str, 
                         params: Dict[str, Any]) -> str:
        """파이 차트 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 데이터 집계
        if 'dataset' in data.columns:
            pie_data = data.groupby('dataset')['value'].sum().reset_index()
            pie_data = pie_data.sort_values('value', ascending=False)
            
            # 상위 8개만 표시 (너무 많으면 복잡해짐)
            if len(pie_data) > 8:
                top_data = pie_data.head(7)
                others_sum = pie_data.tail(len(pie_data) - 7)['value'].sum()
                others_row = pd.DataFrame({'dataset': ['기타'], 'value': [others_sum]})
                pie_data = pd.concat([top_data, others_row], ignore_index=True)
            
            wedges, texts, autotexts = ax.pie(pie_data['value'], 
                                            labels=pie_data['dataset'],
                                            autopct='%1.1f%%',
                                            startangle=90,
                                            colors=self.color_palettes['pastel'][:len(pie_data)])
            
            # 텍스트 스타일 개선
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_scatter_plot(self, data: pd.DataFrame, title: str, 
                           params: Dict[str, Any]) -> str:
        """산점도 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        if len(data.columns) >= 3:  # x, y 값이 있는 경우
            x_col = data.columns[0]
            y_col = data.columns[1]
            
            scatter = ax.scatter(data[x_col], data[y_col], 
                               alpha=0.6, s=60, c=self.color_palettes['default'][0])
            
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_heatmap(self, data: pd.DataFrame, title: str, 
                       params: Dict[str, Any]) -> str:
        """히트맵 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 피벗 테이블 생성
        if 'year' in data.columns and 'dataset' in data.columns:
            pivot_data = data.pivot_table(values='value', 
                                        index='dataset', 
                                        columns='year', 
                                        aggfunc='sum')
            
            sns.heatmap(pivot_data, annot=True, fmt='.0f', 
                       cmap='YlOrRd', ax=ax, cbar_kws={'label': '값'})
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_histogram(self, data: pd.DataFrame, title: str, 
                         params: Dict[str, Any]) -> str:
        """히스토그램 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        ax.hist(data['value'].dropna(), bins=30, alpha=0.7, 
               color=self.color_palettes['default'][0], edgecolor='black')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('값', fontsize=12)
        ax.set_ylabel('빈도', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_box_plot(self, data: pd.DataFrame, title: str, 
                        params: Dict[str, Any]) -> str:
        """박스플롯 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        if 'dataset' in data.columns:
            datasets = data['dataset'].unique()[:8]  # 최대 8개
            box_data = [data[data['dataset'] == dataset]['value'].dropna() 
                       for dataset in datasets]
            
            box_plot = ax.boxplot(box_data, labels=datasets, patch_artist=True)
            
            # 색상 설정
            for patch, color in zip(box_plot['boxes'], self.color_palettes['pastel']):
                patch.set_facecolor(color)
            
            ax.set_xticklabels(datasets, rotation=45, ha='right')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('값', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _create_area_chart(self, data: pd.DataFrame, title: str, 
                          params: Dict[str, Any]) -> str:
        """영역 차트 생성"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        if 'year' in data.columns and 'dataset' in data.columns:
            # 스택 영역 차트
            pivot_data = data.pivot_table(values='value', 
                                        index='year', 
                                        columns='dataset', 
                                        aggfunc='sum', 
                                        fill_value=0)
            
            ax.stackplot(pivot_data.index, 
                        *[pivot_data[col] for col in pivot_data.columns],
                        labels=pivot_data.columns,
                        colors=self.color_palettes['pastel'][:len(pivot_data.columns)],
                        alpha=0.8)
            
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('값', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def _save_plot_to_base64(self, fig) -> str:
        """matplotlib 그래프를 base64 문자열로 변환"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # PIL로 크기 조정
        image = Image.open(buffer)
        image = image.resize((900, 600), Image.Resampling.LANCZOS)
        
        # 다시 buffer에 저장
        resized_buffer = BytesIO()
        image.save(resized_buffer, format='PNG')
        resized_buffer.seek(0)
        
        image_base64 = base64.b64encode(resized_buffer.getvalue()).decode()
        
        plt.close(fig)  # 메모리 정리
        buffer.close()
        resized_buffer.close()
        
        return image_base64
    
    def create_comparison_chart(self, data: pd.DataFrame, 
                              years: List[int], title: str) -> Optional[str]:
        """특정 연도들 간 비교 차트 생성"""
        if not years or len(years) < 2:
            return None
        
        # 지정된 연도들의 데이터만 필터링
        filtered_data = data[data['year'].isin(years)]
        
        if filtered_data.empty:
            return None
        
        self._ensure_korean_font()  # 한글 폰트 재설정
        
        # 이상값 처리 전략 결정
        outlier_strategy = self._determine_outlier_strategy(filtered_data)
        if outlier_strategy != 'none':
            filtered_data = self._detect_and_handle_outliers(filtered_data, outlier_strategy)
        
        if filtered_data.empty:
            print("⚠️ 이상값 제거 후 데이터가 비어있습니다.")
            return None
        
        # 연도별 총배출량 계산
        yearly_totals = filtered_data.groupby('year')['value'].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 스마트 포맷터 적용
        formatter = self._get_smart_formatter(yearly_totals['value'])
        
        bars = ax.bar(yearly_totals['year'].astype(str), yearly_totals['value'],
                     color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(yearly_totals)],
                     alpha=0.8, edgecolor='black', linewidth=1)
        
        # 값 표시 (스마트 포맷팅)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   self._format_value_smart(height),
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('총배출량 (백만톤 CO₂)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Y축 포맷터 적용
        ax.yaxis.set_major_formatter(formatter)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_trend_chart(self, data: pd.DataFrame, title: str) -> Optional[str]:
        """추세 차트 생성"""
        if data.empty:
            return None
        
        self._ensure_korean_font()  # 한글 폰트 재설정
        
        # 이상값 처리 전략 결정
        outlier_strategy = self._determine_outlier_strategy(data)
        if outlier_strategy != 'none':
            data = self._detect_and_handle_outliers(data, outlier_strategy)
        
        if data.empty:
            print("⚠️ 이상값 제거 후 데이터가 비어있습니다.")
            return None
        
        # 연도별 집계
        yearly_data = data.groupby('year')['value'].sum().reset_index()
        yearly_data = yearly_data.sort_values('year')
        
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # 스마트 포맷터 적용
        formatter = self._get_smart_formatter(yearly_data['value'])
        
        ax.plot(yearly_data['year'], yearly_data['value'], 
               marker='o', linewidth=3, markersize=8, 
               color='#1f77b4', markerfacecolor='white', 
               markeredgecolor='#1f77b4', markeredgewidth=2)
        
        # 데이터 포인트에 값 표시
        for _, row in yearly_data.iterrows():
            ax.annotate(self._format_value_smart(row['value']), 
                       (row['year'], row['value']),
                       textcoords="offset points", xytext=(0,10), ha='center',
                       fontsize=9, fontweight='bold')
        
        # 추세선 추가 (데이터가 충분할 때만)
        if len(yearly_data) >= 3:
            try:
                z = np.polyfit(yearly_data['year'], yearly_data['value'], 1)
                p = np.poly1d(z)
                ax.plot(yearly_data['year'], p(yearly_data['year']), 
                       "--", alpha=0.8, color='red', linewidth=2, label='추세선')
                ax.legend()
            except:
                pass  # 추세선 생성 실패해도 계속
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('배출량 (백만톤 CO₂)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Y축 포맷터 적용
        ax.yaxis.set_major_formatter(formatter)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig) 