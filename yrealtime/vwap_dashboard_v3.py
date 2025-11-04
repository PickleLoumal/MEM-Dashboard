import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import time
import os

# Page Configuration
st.set_page_config(
    page_title="Fund Flow Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load Stock List
@st.cache_data(ttl=3600)
def load_stock_list():
    try:
        # Use current date in format MMDD
        today = datetime.now().strftime('%m%d')
        filename = f'List - {today}.xlsx'
        df = pd.read_excel(filename)
        stocks_dict = dict(zip(df['Name '], df['Ticker']))
        return stocks_dict
    except Exception as e:
        st.error(f"Failed to load stock list: {e}")
        return {}

def filter_trading_hours(df):
    """Filter trading hours: 9:15-11:30, 13:00-15:00 (strict filtering)"""
    if df.empty:
        return df
    
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    times = df.index.time
    morning_start = pd.Timestamp('09:15').time()
    morning_end = pd.Timestamp('11:30').time()
    afternoon_start = pd.Timestamp('13:00').time()
    afternoon_end = pd.Timestamp('15:00').time()
    
    # Strict filtering: must be within trading hours
    mask = ((times >= morning_start) & (times <= morning_end)) | \
           ((times >= afternoon_start) & (times <= afternoon_end))
    
    filtered_df = df[mask].copy()
    
    # Additional check: remove any duplicate timestamps and ensure continuous volume
    if not filtered_df.empty:
        filtered_df = filtered_df[~filtered_df.index.duplicated(keep='first')]
    
    return filtered_df

def calculate_vwap(df):
    """Calculate VWAP Indicator"""
    df = df.copy()
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TP_Volume'] = df['Typical_Price'] * df['Volume']
    df['Cumulative_TP_Volume'] = df['TP_Volume'].cumsum()
    df['Cumulative_Volume'] = df['Volume'].cumsum()
    df['VWAP'] = df['Cumulative_TP_Volume'] / df['Cumulative_Volume']
    return df

def calculate_indicators(df):
    """Calculate Technical Indicators: MA5, MA10, OBV, CMF"""
    df = df.copy()
    
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    
    df['OBV'] = 0.0
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] + df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] - df['Volume'].iloc[i]
        else:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1]
    
    df['OBV_MA5'] = df['OBV'].rolling(window=5).mean()
    df['OBV_MA10'] = df['OBV'].rolling(window=10).mean()
    
    df['MF_Multiplier'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df.loc[df['High'] == df['Low'], 'MF_Multiplier'] = 0
    df['MF_Volume'] = df['MF_Multiplier'] * df['Volume']
    df['CMF'] = df['MF_Volume'].rolling(window=21).sum() / df['Volume'].rolling(window=21).sum()
    
    return df

def get_intraday_data(symbol):
    """Get Intraday Minute-level Data"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period='1d', interval='1m')
        
        if df.empty:
            return None
        
        df = df[df['Volume'] > 0]
        df = filter_trading_hours(df)
        
        return df
    except Exception as e:
        st.error(f"Failed to get intraday data: {e}")
        return None

def get_historical_data(symbol):
    """Get Historical Data - 60 trading days for calculation, display last 30 trading days"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period='90d', interval='1d')
        
        if df.empty:
            return None
        
        # Filter only trading days (with volume > 0)
        df = df[df['Volume'] > 0].copy()
        
        # Get last 60 trading days for calculation
        df_full = df.tail(60).copy()
        df_full = calculate_indicators(df_full)
        
        # Display last 30 trading days
        df_display = df_full.tail(30).copy()
        
        # Keep date as a column and add trading day index
        df_display = df_display.reset_index()
        df_display['Date_Str'] = df_display['Date'].dt.strftime('%Y-%m-%d')
        df_display['Trading_Day'] = range(1, len(df_display) + 1)
        
        return df_display
    except Exception as e:
        st.error(f"Failed to get historical data: {e}")
        return None

def create_intraday_chart(df, symbol, company_name):
    """Create Intraday Chart: Candlestick + VWAP + Opening Price Line (without lunch break gap)"""
    if df is None or df.empty:
        return None
    
    df = calculate_vwap(df)
    open_price = df['Open'].iloc[0]
    
    # Save the datetime index before resetting
    datetime_index = df.index
    
    # Create continuous x-axis (remove lunch break gap)
    df = df.reset_index()
    df['Minute_Index'] = range(len(df))
    
    # Create time labels for x-axis (show actual time)
    time_labels = datetime_index.strftime('%H:%M').tolist()
    
    # Select ticks to show (every 30 minutes)
    tick_positions = []
    tick_labels = []
    for i in range(0, len(df), 30):
        tick_positions.append(i)
        tick_labels.append(time_labels[i])
    
    fig = go.Figure()
    
    # Add Candlestick Chart (Red for up, Green for down)
    fig.add_trace(go.Candlestick(
        x=df['Minute_Index'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='red',
        decreasing_line_color='green',
        increasing_fillcolor='red',
        decreasing_fillcolor='green',
        text=time_labels,
        hovertext=[f"Time: {t}<br>Open: {o:.2f}<br>High: {h:.2f}<br>Low: {l:.2f}<br>Close: {c:.2f}" 
                   for t, o, h, l, c in zip(time_labels, df['Open'], df['High'], df['Low'], df['Close'])],
        hoverinfo='text'
    ))
    
    # Add VWAP Line
    fig.add_trace(go.Scatter(
        x=df['Minute_Index'],
        y=df['VWAP'],
        mode='lines',
        name='VWAP',
        line=dict(color='orange', width=2.5),
        hovertemplate='VWAP: %{y:.2f}<extra></extra>'
    ))
    
    # Add Opening Price Horizontal Line
    fig.add_hline(
        y=open_price,
        line_dash="dash",
        line_color="gray",
        line_width=1.5,
        annotation_text=f"Opening: {open_price:.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f'{company_name} ({symbol}) - Intraday Trend (1-Minute)',
        xaxis_title='Time',
        yaxis_title='Price',
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        height=600,
        xaxis=dict(
            tickmode='array',
            tickvals=tick_positions,
            ticktext=tick_labels,
            tickangle=-45
        )
    )
    
    return fig

def create_30day_charts(df, symbol, company_name):
    """Create 30-Day Triple Chart: Candlestick+MA, CMF, OBV+MA (date labels on x-axis)"""
    if df is None or df.empty:
        return None
    
    # Use Trading_Day for x-axis positions, but show dates as labels
    x_axis = df['Trading_Day']
    dates = df['Date_Str']  # Date strings for x-axis labels
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            f'{company_name} ({symbol}) - Price Trend (30 Trading Days)',
            'CMF (Chaikin Money Flow)',
            'OBV (On Balance Volume)'
        ),
        row_heights=[0.5, 0.25, 0.25]
    )
    
    fig.add_trace(go.Candlestick(
        x=x_axis,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
        increasing_line_color='red',
        decreasing_line_color='green',
        increasing_fillcolor='red',
        decreasing_fillcolor='green',
        showlegend=True
    ), row=1, col=1)
    
    # Add Close Price Line (Blue)
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['Close'],
        mode='lines', name='Close Price',
        line=dict(color='blue', width=2.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['MA5'],
        mode='lines', name='MA5',
        line=dict(color='orange', width=2, dash='dash')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['MA10'],
        mode='lines', name='MA10',
        line=dict(color='purple', width=2, dash='dot')
    ), row=1, col=1)
    
    # CMF - Split into positive and negative with proper fills
    cmf_values = df['CMF'].values
    cmf_colors = []
    
    for val in cmf_values:
        if val >= 0:
            cmf_colors.append('rgba(255,0,0,0.2)')  # Red for positive (inflow)
        else:
            cmf_colors.append('rgba(0,255,0,0.2)')  # Green for negative (outflow)
    
    # Draw CMF bars instead of line with fill (no individual hover)
    for i in range(len(x_axis)):
        fig.add_trace(go.Bar(
            x=[x_axis.iloc[i]],
            y=[cmf_values[i]],
            marker_color=cmf_colors[i],
            showlegend=False,
            hoverinfo='skip',
            width=0.8
        ), row=2, col=1)
    
    # CMF line (purple) - drawn on top
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=df['CMF'],
        mode='lines',
        name='CMF',
        line=dict(color='purple', width=2.5),
        showlegend=True
    ), row=2, col=1)
    
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1, row=2, col=1)
    fig.add_hline(y=0.05, line_dash="dash", line_color="green", line_width=1, row=2, col=1)
    fig.add_hline(y=-0.05, line_dash="dash", line_color="red", line_width=1, row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['OBV'],
        mode='lines', name='OBV',
        line=dict(color='red', width=2.5)
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['OBV_MA5'],
        mode='lines', name='OBV MA5',
        line=dict(color='darkblue', width=2, dash='dash')
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['OBV_MA10'],
        mode='lines', name='OBV MA10',
        line=dict(color='green', width=2, dash='dot')
    ), row=3, col=1)
    
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="CMF", row=2, col=1)
    fig.update_yaxes(title_text="OBV", row=3, col=1)
    
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
    
    # Set x-axis to show dates instead of trading day numbers
    fig.update_xaxes(
        tickmode='array',
        tickvals=x_axis,
        ticktext=dates,
        tickangle=-45
    )
    
    fig.update_layout(
        height=1200,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

# Main Program
st.title("Fund Flow Analysis Dashboard")

stocks_dict = load_stock_list()

if not stocks_dict:
    st.error("Unable to load stock list")
    st.stop()

st.sidebar.header("Stock Selection")
selected_name = st.sidebar.selectbox(
    "Select Stock",
    options=list(stocks_dict.keys())
)
selected_symbol = stocks_dict[selected_name]

st.sidebar.info(f"**{selected_name}**\nTicker: {selected_symbol}")

time_period = st.sidebar.radio(
    "Time Period",
    options=["Intraday", "30 Days"],
    index=0
)

auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)

# Main content area
if time_period == "Intraday":
    st.header(f"{selected_name} - Intraday Trend")
    
    with st.spinner("Loading intraday data..."):
        intraday_df = get_intraday_data(selected_symbol)
    
    if intraday_df is not None and not intraday_df.empty:
        latest = intraday_df.iloc[-1]
        first = intraday_df.iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Current Price", f"{latest['Close']:.2f}")
        with col2:
            change = latest['Close'] - first['Open']
            change_pct = (change / first['Open']) * 100
            st.metric("Change", f"{change:+.2f}", f"{change_pct:+.2f}%")
        with col3:
            st.metric("High", f"{intraday_df['High'].max():.2f}")
        with col4:
            st.metric("Low", f"{intraday_df['Low'].min():.2f}")
        with col5:
            st.metric("Update Time", datetime.now().strftime("%H:%M:%S"))
        
        chart = create_intraday_chart(intraday_df, selected_symbol, selected_name)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No trading data available today or market is closed")

else:  # 30 Days
    st.header(f"📈 {selected_name} - 30-Day Trend Analysis")
    
    with st.spinner("Loading historical data..."):
        historical_df = get_historical_data(selected_symbol)
    
    if historical_df is not None and not historical_df.empty:
        latest = historical_df.iloc[-1]
        prev = historical_df.iloc[-2] if len(historical_df) > 1 else latest
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Latest Close", f"{latest['Close']:.2f}")
        with col2:
            change = latest['Close'] - prev['Close']
            change_pct = (change / prev['Close']) * 100 if prev['Close'] != 0 else 0
            st.metric("Change", f"{change:+.2f}", f"{change_pct:+.2f}%")
        with col3:
            cmf_value = latest['CMF'] if pd.notna(latest['CMF']) else 0
            st.metric("CMF", f"{cmf_value:.4f}")
        with col4:
            st.metric("OBV", f"{int(latest['OBV']):,}")
        with col5:
            st.metric("Trading Days", f"{len(historical_df)}")
        
        chart = create_30day_charts(historical_df, selected_symbol, selected_name)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("Unable to retrieve historical data")

if auto_refresh and time_period == "Intraday":
    time.sleep(30)
    st.rerun()