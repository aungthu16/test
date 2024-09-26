import streamlit as st
from streamlit.elements import markdown
import yfinance as yf
import math

st.set_page_config(
    page_title='Stock Analysis Dashboard',
    page_icon=':chart_with_upwards_trend:',
)

@st.cache_data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='max')

    if data.empty:
        raise ValueError("No data found for this ticker.")

    name = stock.info.get('longName','N/A')
    sector = stock.info.get('sector','N/A')
    industry = stock.info.get('industry','N/A')
    employee = stock.info.get('fullTimeEmployees','N/A')
    marketCap = stock.info.get('marketCap','N/A')
    price = stock.info.get('currentPrice', 'N/A')
    previous_close = data['Close'].iloc[-2]
    beta = stock.info.get('beta', 'N/A')
    longProfile = stock.info.get('longBusinessSummary','N/A')
    eps = stock.info.get('trailingEps','N/A')
    pegRatio = stock.info.get('pegRatio','N/A')
    
    change_dollar = price - previous_close
    change_percent = (change_dollar / previous_close) * 100

    return price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap,longProfile, eps, pegRatio

'''
# :chart_with_upwards_trend: Stock Analysis Dashboard

Browse stock data and view the latest market trends.
'''

''
''

ticker = st.text_input("Enter US Stock Ticker:", "AAPL")

if st.button("Submit"):
    try:
        price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio = get_stock_data(ticker)

        st.header(f'{name}', divider='gray')
        profile_cols = st.columns(4)

        profile_cols[0].metric(label='Sector', value=f'{sector}')
        profile_cols[1].metric(label='Industry', value=f'{industry}')
        employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}'
        profile_cols[2].metric(label='Employees', value=f'{employee_value}')
        marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}'
        profile_cols[3].metric(label='Market Cap', value=f'{marketCap_value} M')

        st.write(f'{longProfile}')

        st.header('Stock Performance', divider='gray')
        cols = st.columns(4)

        cols[0].metric(
            label=f'{ticker.upper()} Current Price',
            value=f'${price:,.2f}',
            delta=f'{change_dollar:,.2f} ({change_percent:.2f}%)',
            delta_color='normal' 
        )

        eps_value = 'N/A' if eps == 'N/A' else f'{eps:,.2f}'
        cols[1].metric(
            label='EPS (ttm)',
            value=eps_value
        )
        
        pegRatio_value = 'N/A' if pegRatio == 'N/A' else f'{pegRatio:,.2f}'
        cols[2].metric(
            label='PEG Ratio',
            value=pegRatio_value
        )

        beta_value = 'N/A' if beta == 'N/A' else f'{beta:.2f}'
        cols[3].metric(
            label='Beta',
            value=beta_value
        )
        
    except Exception as e:
        st.error(f"Failed to fetch data. {str(e)}")

''
''
''

st.info('Data provided by Yahoo Finance')
