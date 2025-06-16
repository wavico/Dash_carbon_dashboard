import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Initialize Dash app with enterprise features
app = dash.Dash(__name__, 
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                suppress_callback_exceptions=True,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# App title for browser tab
app.title = "탄소배출량 및 배출권 현황 대시보드"

# Custom CSS styling
custom_style = {
    'backgroundColor': '#f8f9fa',
    'fontFamily': 'Arial, sans-serif'
}

header_style = {
    'textAlign': 'center',
    'color': '#2E4057',
    'fontSize': '28px',
    'fontWeight': 'bold',
    'marginBottom': '30px',
    'padding': '20px'
}

filter_container_style = {
    'backgroundColor': '#ffffff',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

chart_container_style = {
    'backgroundColor': '#ffffff',
    'padding': '15px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

# Data generation function (same as Streamlit version)
def generate_sample_data():
    """Generate comprehensive sample data for the dashboard"""
    # Time range setup
    years = list(range(2020, 2025))
    months = list(range(1, 13))
    
    # Regional data with coordinates
    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    coords = {
        '서울': (37.5665, 126.9780), '부산': (35.1796, 129.0756), '대구': (35.8714, 128.6014),
        '인천': (37.4563, 126.7052), '광주': (35.1595, 126.8526), '대전': (36.3504, 127.3845),
        '울산': (35.5384, 129.3114), '세종': (36.4800, 127.2890), '경기': (37.4138, 127.5183),
        '강원': (37.8228, 128.1555), '충북': (36.8, 127.7), '충남': (36.5184, 126.8000),
        '전북': (35.7175, 127.153), '전남': (34.8679, 126.991), '경북': (36.4919, 128.8889),
        '경남': (35.4606, 128.2132), '제주': (33.4996, 126.5312)
    }
    
    # 1. Regional CO2 concentration data
    regions_data = []
    for year in years:
        for month in months:
            for region in regions:
                base_co2 = np.random.uniform(410, 430)
                seasonal_effect = np.sin((month-1)/12*2*np.pi) * 5
                yearly_trend = (year - 2020) * 2
                
                regions_data.append({
                    '지역명': region,
                    '평균_이산화탄소_농도': base_co2 + seasonal_effect + yearly_trend + np.random.uniform(-3, 3),
                    '연도': year,
                    '월': month,
                    '연월': f"{year}-{month:02d}",
                    'lat': coords[region][0],
                    'lon': coords[region][1]
                })
    
    # 2. Annual emissions data
    emissions_data = []
    for year in years:
        emissions_data.append({
            '연도': year,
            '총배출량': 650000 + (year-2020)*15000 + np.random.randint(-10000, 10000),
            '특정산업배출량': 200000 + (year-2020)*8000 + np.random.randint(-5000, 5000)
        })
    
    # 3. Market data (price/volume)
    market_data = []
    for year in years:
        for month in months:
            market_data.append({
                '연도': year,
                '월': month,
                '연월': f"{year}-{month:02d}",
                '시가': 10000 + np.random.randint(-2000, 3000) + (year-2020)*500,
                '거래량': 5000 + np.random.randint(-1000, 2000) + month*100
            })
    
    # 4. Company allocation data
    companies = ['포스코홀딩스', '현대제철', 'SK이노베이션', 'LG화학', '삼성전자', 'SK하이닉스', '한화솔루션', 'GS칼텍스', 'S-Oil', '롯데케미칼']
    industries = ['철강', '철강', '석유화학', '화학', '전자', '반도체', '화학', '정유', '정유', '화학']
    
    treemap_data = []
    for year in years:
        for i, company in enumerate(companies):
            treemap_data.append({
                '연도': year,
                '업체명': company,
                '업종': industries[i],
                '대상년도별할당량': np.random.randint(50000, 200000) + (year-2020)*5000
            })
    
    # 5. Time series data
    time_series_data = []
    for year in years:
        for month in months:
            for region in ['서울', '부산', '대구', '인천', '광주']:
                base_co2 = np.random.uniform(410, 425)
                seasonal_effect = np.sin((month-1)/12*2*np.pi) * 3
                yearly_trend = (year - 2020) * 1.5
                
                time_series_data.append({
                    '지역명': region,
                    '연도': year,
                    '월': month,
                    '연월': f"{year}-{month:02d}",
                    '평균_이산화탄소_농도': base_co2 + seasonal_effect + yearly_trend + np.random.uniform(-2, 2)
                })
    
    # 6. Gauge data
    gauge_data = []
    for year in years:
        for month in months:
            gauge_data.append({
                '연도': year,
                '월': month,
                '연월': f"{year}-{month:02d}",
                '탄소배출권_보유수량': np.random.randint(800000, 1200000) + (year-2020)*50000,
                '현재_탄소배출량': np.random.randint(600000, 900000) + (year-2020)*30000
            })
    
    return (
        pd.DataFrame(regions_data),
        pd.DataFrame(emissions_data),
        pd.DataFrame(market_data),
        pd.DataFrame(treemap_data),
        pd.DataFrame(time_series_data),
        pd.DataFrame(gauge_data)
    )

# Generate data
regions_df, emissions_df, market_df, treemap_df, timeseries_df, gauge_df = generate_sample_data()

# App layout
app.layout = html.Div([
    # Header
    html.H1("🌍 탄소배출량 및 배출권 현황", style=header_style),
    
    # Main container
    html.Div([
        # Left column
        html.Div([
            # Filter section
            html.Div([
                html.H3("🔍 필터 설정", style={'marginBottom': '20px', 'color': '#2E4057'}),
                
                html.Div([
                    html.Div([
                        html.Label("연도 선택", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                        dcc.Slider(
                            id='year-slider',
                            min=int(regions_df['연도'].min()),
                            max=int(regions_df['연도'].max()),
                            value=int(regions_df['연도'].max()),
                            marks={year: str(year) for year in range(2020, 2025)},
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.Label("월 선택", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                        dcc.Slider(
                            id='month-slider',
                            min=1,
                            max=12,
                            value=1,
                            marks={i: f"{i}월" for i in range(1, 13)},
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
                ])
            ], style=filter_container_style),
            
            # Gauge charts
            html.Div([
                html.H3("📊 현황 지표", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='gauge-charts')
            ], style=chart_container_style),
            
            # Map chart
            html.Div([
                html.H3("🗺️ 지역별 이산화탄소 농도 현황", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='map-chart')
            ], style=chart_container_style)
            
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '2%'}),
        
        # Right column
        html.Div([
            # Emissions bar chart
            html.Div([
                html.H3("📊 연도별 탄소 배출량 현황", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='emissions-chart')
            ], style=chart_container_style),
            
            # Market combo chart
            html.Div([
                html.H3("💹 KAU24 시가/거래량", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='market-chart')
            ], style=chart_container_style),
            
            # Treemap
            html.Div([
                html.H3("🏭 업체별 할당량 현황", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='treemap-chart')
            ], style=chart_container_style),
            
            # Time series
            html.Div([
                html.H3("📈 지역별 이산화탄소 농도 시계열", style={'marginBottom': '20px', 'color': '#2E4057'}),
                dcc.Graph(id='timeseries-chart')
            ], style=chart_container_style)
            
        ], style={'width': '53%', 'float': 'right', 'display': 'inline-block', 'verticalAlign': 'top'})
        
    ], style={'padding': '20px'}),
    
    # Footer
    html.Hr(),
    html.Div([
        html.P("🌍 탄소배출량 및 배출권 현황 대시보드 | Built with Plotly Dash Enterprise",
               style={'textAlign': 'center', 'color': '#888', 'marginTop': '50px'})
    ])
    
], style=custom_style)

# Callback for gauge charts
@app.callback(
    Output('gauge-charts', 'figure'),
    [Input('year-slider', 'value'),
     Input('month-slider', 'value')]
)
def update_gauge_charts(selected_year, selected_month):
    # Filter gauge data
    gauge_filtered = gauge_df[(gauge_df['연도'] == selected_year) & (gauge_df['월'] == selected_month)]
    
    if gauge_filtered.empty:
        return go.Figure()
    
    emission_allowance = gauge_filtered.iloc[0]['탄소배출권_보유수량']
    current_emission = gauge_filtered.iloc[0]['현재_탄소배출량']
    
    # Create gauge charts
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=('탄소배출권 보유수량', '현재 탄소배출량'),
        horizontal_spacing=0.2
    )
    
    # Emission allowance gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=emission_allowance,
            title={'text': f"보유수량<br><span style='font-size:0.8em;color:gray'>{selected_year}년 {selected_month}월</span>"},
            number={'suffix': " tCO₂eq", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 1500000], 'tickfont': {'size': 10}},
                'bar': {'color': "lightgreen", 'thickness': 0.8},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 500000], 'color': "lightgray"},
                    {'range': [500000, 1000000], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 1200000
                }
            }
        ),
        row=1, col=1
    )
    
    # Current emission gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=current_emission,
            title={'text': f"현재배출량<br><span style='font-size:0.8em;color:gray'>{selected_year}년 {selected_month}월</span>"},
            number={'suffix': " tCO₂eq", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 1200000], 'tickfont': {'size': 10}},
                'bar': {'color': "orange", 'thickness': 0.8},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 400000], 'color': "lightgray"},
                    {'range': [400000, 800000], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 1000000
                }
            }
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(size=12),
        showlegend=False
    )
    
    return fig

# Callback for map chart
@app.callback(
    Output('map-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('month-slider', 'value')]
)
def update_map_chart(selected_year, selected_month):
    # Filter map data
    map_filtered = regions_df[(regions_df['연도'] == selected_year) & (regions_df['월'] == selected_month)]
    
    if map_filtered.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=map_filtered["lat"],
        lon=map_filtered["lon"],
        mode='markers',
        marker=dict(
            size=map_filtered["평균_이산화탄소_농도"] / 15,
            color=map_filtered["평균_이산화탄소_농도"],
            colorscale="Reds",
            showscale=True,
            colorbar=dict(title="CO₂ 농도 (ppm)")
        ),
        text=map_filtered["지역명"],
        hovertemplate="<b>%{text}</b><br>CO₂ 농도: %{marker.color:.1f} ppm<extra></extra>",
        name="지역별 CO₂ 농도"
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=36.5, lon=127.5),
            zoom=6
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        title=f"{selected_year}년 {selected_month}월 지역별 평균 이산화탄소 농도 분포"
    )
    
    return fig

# Callback for emissions chart
@app.callback(
    Output('emissions-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_emissions_chart(selected_year):
    emissions_filtered = emissions_df[emissions_df['연도'] <= selected_year]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=emissions_filtered['연도'],
        y=emissions_filtered['총배출량'],
        name='총배출량',
        marker_color='gold'
    ))
    
    fig.add_trace(go.Bar(
        x=emissions_filtered['연도'],
        y=emissions_filtered['특정산업배출량'],
        name='특정산업배출량',
        marker_color='steelblue'
    ))
    
    fig.update_layout(
        title=f"{selected_year}년까지 연도별 배출량 비교",
        xaxis_title="연도",
        yaxis_title="배출량 (tCO₂eq)",
        barmode='group',
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Callback for market chart
@app.callback(
    Output('market-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_market_chart(selected_year):
    market_filtered = market_df[market_df['연도'] == selected_year]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=market_filtered['월'], y=market_filtered['거래량'], name="거래량", marker_color='steelblue'),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=market_filtered['월'], y=market_filtered['시가'], mode='lines+markers', 
                  name="시가", line=dict(color='gold', width=3)),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="월")
    fig.update_yaxes(title_text="거래량", secondary_y=False)
    fig.update_yaxes(title_text="시가 (원)", secondary_y=True)
    fig.update_layout(title=f"{selected_year}년 월별 시가/거래량 추이", height=300)
    
    return fig

# Callback for treemap chart
@app.callback(
    Output('treemap-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_treemap_chart(selected_year):
    treemap_filtered = treemap_df[treemap_df['연도'] == selected_year]
    
    fig = px.treemap(
        treemap_filtered,
        path=['업종', '업체명'],
        values='대상년도별할당량',
        title=f"{selected_year}년 업종별/업체별 할당량 분포",
        height=300,
        color='대상년도별할당량',
        color_continuous_scale='Viridis'
    )
    
    return fig

# Callback for time series chart
@app.callback(
    Output('timeseries-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_timeseries_chart(selected_year):
    timeseries_filtered = timeseries_df[timeseries_df['연도'] <= selected_year]
    
    fig = px.line(
        timeseries_filtered,
        x='연월',
        y='평균_이산화탄소_농도',
        color='지역명',
        title=f"{selected_year}년까지 월별 지역별 CO₂ 농도 변화",
        height=300,
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="연월",
        yaxis_title="CO₂ 농도 (ppm)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
