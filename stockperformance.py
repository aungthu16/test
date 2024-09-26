import streamlit as st
import yfinance as yf
import math

st.set_page_config(
    page_title='Stock Analysis Dashboard',
    page_icon=':chart_with_upwards_trend:',
)

@st.cache_data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')

    if data.empty:
        raise ValueError("No data found for this ticker.")

    current_price = data['Close'].iloc[0]
    previous_close = data['Close'].shift(1).iloc[0]
    beta = stock.info.get('beta', 'N/A')  

    change_dollar = current_price - previous_close
    change_percent = (change_dollar / previous_close) * 100

    return current_price, change_percent, change_dollar, beta

'''
# :chart_with_upwards_trend: Stock Analysis Dashboard

Browse stock data and view the latest market trends.
'''

''
''

ticker = st.text_input("Enter US Stock Ticker:", "AAPL")

if st.button("Submit"):
    try:
        current_price, change_percent, change_dollar, beta = get_stock_data(ticker)

        st.header('Stock Performance', divider='gray')

        cols = st.columns(4)

        cols[0].metric(
            label=f'{ticker.upper()} Current Price',
            value=f'${current_price:.2f}',
            delta=f'{change_dollar:.2f}',
            delta_color='normal' if change_dollar >= 0 else 'inverse'
        )

        cols[1].metric(
            label='Daily Change %',
            value=f'{change_percent:.2f}%',
            delta=f'{change_dollar:.2f} USD',
            delta_color='normal' if change_percent >= 0 else 'inverse'
        )

        cols[2].metric(
            label='Daily Change $',
            value=f'${change_dollar:.2f}',
            delta=f'{change_percent:.2f}%',
            delta_color='normal' if change_dollar >= 0 else 'inverse'
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
