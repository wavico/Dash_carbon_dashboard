import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="Interactive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 타이틀
st.title("📊 Interactive Data Dashboard")
st.markdown("---")

# 사이드바 - 데이터 업로드 및 설정
with st.sidebar:
    st.header("🔧 Dashboard Controls")
    
    # 데이터 업로드
    st.subheader("📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your data file to create visualizations"
    )
    
    # 샘플 데이터 생성 옵션
    if st.button("🎲 Generate Sample Data"):
        # 샘플 데이터 생성
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        categories = ['Category A', 'Category B', 'Category C', 'Category D']
        regions = ['North', 'South', 'East', 'West']
        
        data = []
        for _ in range(1000):
            data.append({
                'Date': np.random.choice(dates),
                'Category': np.random.choice(categories),
                'Region': np.random.choice(regions),
                'Sales': np.random.normal(1000, 300),
                'Quantity': np.random.randint(1, 100),
                'Profit': np.random.normal(200, 100),
                'Customer_Satisfaction': np.random.uniform(1, 5)
            })
        
        st.session_state['sample_data'] = pd.DataFrame(data)
        st.success("✅ Sample data generated!")

# 데이터 로드
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully! Shape: {df.shape}")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
elif 'sample_data' in st.session_state:
    df = st.session_state['sample_data']

# 메인 대시보드
if df is not None:
    # 데이터 미리보기
    with st.expander("🔍 Data Preview", expanded=False):
        st.dataframe(df.head(), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Data Types", len(df.dtypes.unique()))
    
    # 사이드바 - 시각화 설정
    with st.sidebar:
        st.markdown("---")
        st.subheader("📈 Visualization Settings")
        
        # 컬럼 선택
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        date_columns = []
        
        # 날짜 컬럼 자동 감지
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col])
                    date_columns.append(col)
                except:
                    pass
        
        # 필터 설정
        st.subheader("🔍 Filters")
        filters = {}
        
        for col in categorical_columns[:3]:  # 최대 3개 카테고리컬 컬럼
            if col not in date_columns:
                unique_values = df[col].unique()
                if len(unique_values) <= 20:  # 너무 많은 고유값은 제외
                    selected_values = st.multiselect(
                        f"Filter by {col}",
                        options=unique_values,
                        default=unique_values
                    )
                    filters[col] = selected_values
        
        # 필터 적용
        filtered_df = df.copy()
        for col, values in filters.items():
            if values:
                filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    # 메인 대시보드 레이아웃
    if len(filtered_df) > 0:
        # KPI 섹션
        if numeric_columns:
            st.subheader("📊 Key Performance Indicators")
            kpi_cols = st.columns(min(4, len(numeric_columns)))
            
            for i, col in enumerate(numeric_columns[:4]):
                with kpi_cols[i]:
                    value = filtered_df[col].sum() if filtered_df[col].dtype in ['int64', 'float64'] else len(filtered_df[col].unique())
                    st.metric(
                        label=col.replace('_', ' ').title(),
                        value=f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
                    )
        
        st.markdown("---")
        
        # 차트 섹션
        if len(numeric_columns) >= 1:
            # 첫 번째 행 - 시계열 및 카테고리별 분석
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Time Series Analysis")
                if date_columns and numeric_columns:
                    date_col = date_columns[0]
                    value_col = numeric_columns[0]
                    
                    # 날짜 컬럼 변환
                    temp_df = filtered_df.copy()
                    temp_df[date_col] = pd.to_datetime(temp_df[date_col])
                    
                    # 일별 집계
                    daily_data = temp_df.groupby(temp_df[date_col].dt.date)[value_col].sum().reset_index()
                    
                    fig_line = px.line(
                        daily_data, 
                        x=date_col, 
                        y=value_col,
                        title=f"{value_col} Over Time"
                    )
                    fig_line.update_layout(height=400)
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    # 대체 차트
                    if len(numeric_columns) >= 2:
                        fig_scatter = px.scatter(
                            filtered_df, 
                            x=numeric_columns[0], 
                            y=numeric_columns[1],
                            title=f"{numeric_columns[1]} vs {numeric_columns[0]}"
                        )
                        fig_scatter.update_layout(height=400)
                        st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                st.subheader("📊 Category Analysis")
                if categorical_columns and numeric_columns:
                    cat_col = categorical_columns[0]
                    val_col = numeric_columns[0]
                    
                    # 카테고리별 집계
                    cat_data = filtered_df.groupby(cat_col)[val_col].sum().reset_index()
                    cat_data = cat_data.sort_values(val_col, ascending=False).head(10)
                    
                    fig_bar = px.bar(
                        cat_data, 
                        x=cat_col, 
                        y=val_col,
                        title=f"{val_col} by {cat_col}"
                    )
                    fig_bar.update_layout(height=400)
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        # 두 번째 행 - 분포 및 상관관계
        if len(numeric_columns) >= 2:
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("📈 Distribution Analysis")
                selected_col = st.selectbox(
                    "Select column for distribution",
                    numeric_columns,
                    key="dist_col"
                )
                
                fig_hist = px.histogram(
                    filtered_df, 
                    x=selected_col,
                    title=f"Distribution of {selected_col}",
                    nbins=30
                )
                fig_hist.update_layout(height=400)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col4:
                st.subheader("🎯 Correlation Heatmap")
                # 숫자형 컬럼만 선택
                numeric_df = filtered_df[numeric_columns]
                
                if len(numeric_df.columns) >= 2:
                    corr_matrix = numeric_df.corr()
                    
                    fig_heatmap = px.imshow(
                        corr_matrix,
                        title="Correlation Matrix",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )
                    fig_heatmap.update_layout(height=400)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # 세 번째 행 - 상세 분석
        if len(categorical_columns) >= 2 and len(numeric_columns) >= 1:
            st.subheader("🔍 Detailed Analysis")
            
            col5, col6 = st.columns(2)
            
            with col5:
                # 파이 차트
                if categorical_columns:
                    pie_col = categorical_columns[0]
                    pie_data = filtered_df[pie_col].value_counts().head(8)
                    
                    fig_pie = px.pie(
                        values=pie_data.values,
                        names=pie_data.index,
                        title=f"Distribution of {pie_col}"
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col6:
                # 박스 플롯
                if len(categorical_columns) >= 1 and len(numeric_columns) >= 1:
                    box_cat = categorical_columns[0]
                    box_num = numeric_columns[0]
                    
                    fig_box = px.box(
                        filtered_df,
                        x=box_cat,
                        y=box_num,
                        title=f"{box_num} Distribution by {box_cat}"
                    )
                    fig_box.update_layout(height=400)
                    st.plotly_chart(fig_box, use_container_width=True)
        
        # 데이터 테이블
        st.subheader("📋 Filtered Data")
        st.dataframe(filtered_df, use_container_width=True, height=300)
        
        # 데이터 다운로드
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("⚠️ No data matches the selected filters. Please adjust your filter settings.")

else:
    # 데이터가 없을 때 안내
    st.info("👆 Please upload a CSV file or generate sample data using the sidebar controls to get started!")
    
    # 기능 소개
    st.subheader("🌟 Dashboard Features")
    
    features = [
        "📁 **Data Upload**: Upload your CSV files for instant visualization",
        "🎲 **Sample Data**: Generate sample data to explore dashboard features",
        "🔍 **Interactive Filters**: Filter data by categories to focus on specific segments",
        "📊 **Multiple Chart Types**: Line charts, bar charts, scatter plots, heatmaps, and more",
        "📈 **Time Series Analysis**: Automatic detection and visualization of time-based data",
        "🎯 **Correlation Analysis**: Understand relationships between variables",
        "📋 **Data Export**: Download filtered data for further analysis",
        "📱 **Responsive Design**: Works on desktop and mobile devices"
    ]
    
    for feature in features:
        st.markdown(feature)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888;'>
        <p>Built with ❤️ using Streamlit and Plotly | Interactive Data Dashboard v1.0</p>
    </div>
    """, 
    unsafe_allow_html=True
)
