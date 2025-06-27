"""
안전한 코드 실행 환경
사용자 질문을 pandas/numpy 코드로 변환하고 안전하게 실행
"""

import ast
import sys
import io
import contextlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import warnings
import traceback
from datetime import datetime
import re

class SafeCodeExecutor:
    """안전한 코드 실행 클래스"""
    
    def __init__(self):
        """코드 실행기 초기화"""
        # 허용된 모듈과 함수들
        self.allowed_modules = {
            'pandas': pd,
            'numpy': np,
            'matplotlib.pyplot': plt,
            'seaborn': sns,
            'datetime': datetime
        }
        
        # 허용된 내장 함수들
        self.allowed_builtins = {
            'len', 'sum', 'max', 'min', 'abs', 'round', 'int', 'float', 'str',
            'list', 'dict', 'tuple', 'set', 'range', 'enumerate', 'zip',
            'sorted', 'reversed', 'any', 'all', 'print'
        }
        
        # 금지된 키워드와 함수들
        self.forbidden_keywords = {
            'import', 'exec', 'eval', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload', 'globals', 'locals', 'vars',
            'dir', 'hasattr', 'getattr', 'setattr', 'delattr', '__builtins__'
        }
        
        # 코드 실행 히스토리
        self.execution_history: List[Dict[str, Any]] = []
        
    def generate_code_from_query(self, query: str, data_info: Dict[str, Any]) -> str:
        """질문을 바탕으로 pandas 코드 생성"""
        query_lower = query.lower()
        
        # 기본 데이터프레임 이름
        df_name = "unified_data"
        
        code_lines = [
            f"# 질문: {query}",
            f"# 생성된 코드",
            ""
        ]
        
        # 연도 필터링
        years = self._extract_years(query)
        if years:
            if len(years) == 1:
                code_lines.append(f"filtered_data = {df_name}[{df_name}['year'] == {years[0]}]")
            else:
                year_list = str(years)
                code_lines.append(f"filtered_data = {df_name}[{df_name}['year'].isin({year_list})]")
        else:
            code_lines.append(f"filtered_data = {df_name}.copy()")
        
        # 집계 타입 결정
        if any(word in query_lower for word in ['총', '합계', '전체']):
            aggregation = 'sum'
        elif any(word in query_lower for word in ['평균']):
            aggregation = 'mean'
        elif any(word in query_lower for word in ['최대', '최고']):
            aggregation = 'max'
        elif any(word in query_lower for word in ['최소', '최저']):
            aggregation = 'min'
        else:
            aggregation = 'sum'
        
        # 비교 질문인지 확인
        if any(word in query_lower for word in ['비교', '차이', '대비']):
            if years and len(years) >= 2:
                code_lines.extend([
                    "",
                    "# 연도별 총합 계산",
                    f"yearly_totals = filtered_data.groupby('year')['value'].{aggregation}().reset_index()",
                    "result = yearly_totals",
                    "print('연도별 총합:')",
                    "print(result)"
                ])
            else:
                code_lines.extend([
                    "",
                    "# 데이터셋별 총합 계산", 
                    f"dataset_totals = filtered_data.groupby('dataset')['value'].{aggregation}().reset_index()",
                    "result = dataset_totals.sort_values('value', ascending=False)",
                    "print('데이터셋별 총합:')",
                    "print(result)"
                ])
        
        # 추세 질문인지 확인
        elif any(word in query_lower for word in ['추이', '변화', '트렌드', '경향']):
            code_lines.extend([
                "",
                "# 연도별 추세 계산",
                f"trend_data = filtered_data.groupby('year')['value'].{aggregation}().reset_index()",
                "trend_data = trend_data.sort_values('year')",
                "result = trend_data",
                "print('연도별 추세:')",
                "print(result)"
            ])
        
        # 순위 질문인지 확인
        elif any(word in query_lower for word in ['순위', '많은', '적은', '높은', '낮은']):
            ascending = any(word in query_lower for word in ['적은', '낮은', '최소'])
            code_lines.extend([
                "",
                "# 순위 계산",
                f"ranking_data = filtered_data.groupby('dataset')['value'].{aggregation}().reset_index()",
                f"ranking_data = ranking_data.sort_values('value', ascending={ascending})",
                "result = ranking_data",
                "print('순위별 데이터:')",
                "print(result)"
            ])
        
        # 특정 값 조회
        else:
            code_lines.extend([
                "",
                "# 데이터 요약",
                f"summary = filtered_data.groupby(['year', 'dataset'])['value'].{aggregation}().reset_index()",
                "result = summary",
                "print('데이터 요약:')",
                "print(result.head(10))"
            ])
        
        return "\n".join(code_lines)
    
    def _extract_years(self, query: str) -> List[int]:
        """질문에서 연도 추출"""
        years = []
        year_pattern = r'(\d{4})'
        matches = re.findall(year_pattern, query)
        
        for match in matches:
            year = int(match)
            if 1990 <= year <= 2030:
                years.append(year)
        
        return sorted(list(set(years)))
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """코드 안전성 검증"""
        try:
            # AST 파싱으로 구문 오류 확인
            tree = ast.parse(code)
            
            # 금지된 키워드 확인
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id in self.forbidden_keywords:
                        return False, f"금지된 키워드 사용: {node.id}"
                
                # import 문 확인
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False, "import 문은 허용되지 않습니다"
                
                # 함수 호출 확인
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.forbidden_keywords:
                            return False, f"금지된 함수 호출: {node.func.id}"
            
            return True, "코드가 안전합니다"
            
        except SyntaxError as e:
            return False, f"구문 오류: {e}"
        except Exception as e:
            return False, f"검증 오류: {e}"
    
    def execute_code(self, code: str, context: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """
        코드를 안전하게 실행
        
        Args:
            code: 실행할 코드
            context: 실행 컨텍스트 (데이터프레임 등)
            
        Returns:
            (성공여부, 결과, 출력/오류메시지)
        """
        # 코드 검증
        is_safe, message = self.validate_code(code)
        if not is_safe:
            return False, None, f"코드 검증 실패: {message}"
        
        # 실행 컨텍스트 준비
        exec_context = self._prepare_context(context)
        
        # 출력 캡처 준비
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    
                    # 코드 실행
                    exec(code, {"__builtins__": {}}, exec_context)
            
            # 결과 추출
            result = exec_context.get('result', None)
            output = output_buffer.getvalue()
            
            # 실행 히스토리 저장
            self._save_execution_history(code, result, output, True)
            
            return True, result, output
            
        except Exception as e:
            error_msg = f"실행 오류: {str(e)}\n{traceback.format_exc()}"
            self._save_execution_history(code, None, error_msg, False)
            return False, None, error_msg
        
        finally:
            output_buffer.close()
    
    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """실행 컨텍스트 준비"""
        exec_context = {}
        
        # 허용된 모듈들 추가
        exec_context.update(self.allowed_modules)
        
        # 허용된 내장 함수들 추가
        for builtin_name in self.allowed_builtins:
            if hasattr(__builtins__, builtin_name):
                exec_context[builtin_name] = getattr(__builtins__, builtin_name)
        
        # 사용자 제공 컨텍스트 추가
        exec_context.update(context)
        
        return exec_context
    
    def _save_execution_history(self, code: str, result: Any, output: str, success: bool):
        """실행 히스토리 저장"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'result': str(result) if result is not None else None,
            'output': output,
            'success': success
        }
        
        self.execution_history.append(history_entry)
        
        # 히스토리 크기 제한 (최대 100개)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def generate_analysis_code(self, query_intent: Any, data_columns: List[str]) -> str:
        """질문 의도를 바탕으로 분석 코드 생성"""
        code_lines = [
            "# 자동 생성된 분석 코드",
            f"# 질문 타입: {query_intent.query_type.value}",
            ""
        ]
        
        # 기본 필터링
        if query_intent.years:
            year_filter = f"unified_data['year'].isin({query_intent.years})"
            code_lines.append(f"filtered_data = unified_data[{year_filter}]")
        else:
            code_lines.append("filtered_data = unified_data.copy()")
        
        # 질문 타입별 분석 코드
        if query_intent.query_type.value == 'comparison':
            code_lines.extend([
                "",
                "# 비교 분석",
                f"comparison_result = filtered_data.groupby('year')['value'].{query_intent.aggregation}().reset_index()",
                "result = comparison_result",
                "print('비교 결과:')",
                "print(result)"
            ])
        
        elif query_intent.query_type.value == 'trend':
            code_lines.extend([
                "",
                "# 추세 분석",
                "trend_result = filtered_data.groupby('year')['value'].sum().reset_index()",
                "trend_result = trend_result.sort_values('year')",
                "result = trend_result",
                "print('추세 분석 결과:')",
                "print(result)"
            ])
        
        elif query_intent.query_type.value == 'ranking':
            code_lines.extend([
                "",
                "# 순위 분석",
                "ranking_result = filtered_data.groupby('dataset')['value'].sum().reset_index()",
                "ranking_result = ranking_result.sort_values('value', ascending=False)",
                "result = ranking_result",
                "print('순위 분석 결과:')",
                "print(result)"
            ])
        
        else:
            code_lines.extend([
                "",
                "# 기본 분석",
                "basic_result = filtered_data.groupby(['year', 'dataset'])['value'].sum().reset_index()",
                "result = basic_result",
                "print('분석 결과:')",
                "print(result.head(10))"
            ])
        
        return "\n".join(code_lines)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """실행 요약 정보 반환"""
        if not self.execution_history:
            return {"total_executions": 0, "success_rate": 0, "recent_executions": []}
        
        total = len(self.execution_history)
        successful = sum(1 for entry in self.execution_history if entry['success'])
        success_rate = successful / total if total > 0 else 0
        
        recent = self.execution_history[-5:]  # 최근 5개
        
        return {
            "total_executions": total,
            "success_rate": success_rate,
            "recent_executions": recent
        }
    
    def clear_history(self):
        """실행 히스토리 초기화"""
        self.execution_history = []
    
    def debug_code(self, code: str) -> List[str]:
        """코드 디버깅 정보 제공"""
        debug_info = []
        
        try:
            tree = ast.parse(code)
            
            # 변수 사용 분석
            variables = set()
            functions = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    variables.add(node.id)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    functions.add(node.func.id)
            
            debug_info.append(f"사용된 변수: {', '.join(sorted(variables))}")
            debug_info.append(f"호출된 함수: {', '.join(sorted(functions))}")
            
            # 코드 복잡도 분석
            lines = [line.strip() for line in code.split('\n') if line.strip()]
            debug_info.append(f"코드 라인 수: {len(lines)}")
            
        except Exception as e:
            debug_info.append(f"디버깅 분석 오류: {e}")
        
        return debug_info 