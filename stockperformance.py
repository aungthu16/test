import streamlit as st
from streamlit.elements import markdown
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import math

st.set_page_config(
    page_title='Stock Analysis Dashboard',
    page_icon=':chart_with_upwards_trend:',
)

@st.cache_data
def get_stock_data(ticker):
    
    lowercase_ticker = ticker.lower()
    picture_url = "https://logos.stockanalysis.com/" + lowercase_ticker + ".svg"
    
    sa_analysts_url = "https://stockanalysis.com/stocks/" + ticker + "/statistics/"
    sa_analysts_response = requests.get(sa_analysts_url)
    sa_analysts_soup = BeautifulSoup(sa_analysts_response.content, "html.parser")
    sa_analyst_table = sa_analysts_soup.find_all('table')[15]
    sa_analysts_data = {}
    sa_analysts_consensus = "N/A"
    sa_analysts_targetprice = "N/A"
    sa_analysts_count = "N/A"
    
    if sa_analyst_table:
            rows = sa_analyst_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:  
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    sa_analysts_data[key] = value

            sa_analysts_consensus = sa_analysts_data.get("Analyst Consensus", "N/A")
            sa_analysts_targetprice = sa_analysts_data.get("Price Target", "N/A")
            sa_analysts_count = sa_analysts_data.get("Analyst Count", "N/A")
    else: 
            print("SA analyst table not found on the page")
    
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
    country = stock.info.get('country', 'N/A')
    yf_targetprice = stock.info.get(' targetMeanPrice','N/A')
    yf_consensus = stock.info.get(' recommendationKey','N/A')
    yf_analysts_count = stock.info.get('  numberOfAnalystOpinions','N/A')
    website = stock.info.get('website','N/A')
    
    
    change_dollar = price - previous_close
    change_percent = (change_dollar / previous_close) * 100

    return price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap,longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website

'''
# :chart_with_upwards_trend: Stock Analysis Dashboard

Browse stock data and view the latest market trends.
'''

''
''

ticker = st.text_input("Enter US Stock Ticker:", "AAPL")

if st.button("Submit"):
    try:
        price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website = get_stock_data(ticker)

        st.header(f'{name}', divider='gray')
        
        employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}'
        marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}'

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"""
            <div style='text-align: left;'>
                <img src='{picture_url}' style='width:100%; max-width:150px; height:auto;'>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style='float: right;'>
                <table>
                    <tr><td><strong>Sector</strong></td><td>{sector}</td></tr>
                    <tr><td><strong>Industry</strong></td><td>{industry}</td></tr>
                    <tr><td><strong>Employees</strong></td><td>{employee_value}</td></tr>
                    <tr><td><strong>Market Cap</strong></td><td>{marketCap_value}</td></tr>
                    <tr><td><strong>Country</strong></td><td>{country}</td></tr>
                    <tr><td><strong>Website</strong></td><td>{website}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"<div style='text-align: justify;'>{longProfile}</div>", unsafe_allow_html=True)

        ''
        ''

        st.subheader('Stock Performance', divider='gray')
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

        st.subheader('Anslysts Ratings', divider='gray')

        col1, col2 = st.columns([3, 3])
        with col1:
            st.markdown(f"""
            <table>
                <tr><td><strong>SA Price Target</strong></td><td>{sa_analysts_targetprice}</td></tr>
                <tr><td><strong>SA Analyst Consensus</strong></td><td>{sa_analysts_consensus}</td></tr>
                <tr><td><strong>SA Analyst Count</strong></td><td>{sa_analysts_count}</td></tr>
            </table>
            """, unsafe_allow_html=True)

        yf_targetprice_value = 'N/A' if yf_targetprice == 'N/A' else f'${yf_targetprice:,2f}'

        with col2:
            st.markdown(f"""
            <table>
                <tr><td><strong>YF Price Target</strong></td><td>{yf_targetprice_value}</td></tr>
                <tr><td><strong>YF Analyst Consensus</strong></td><td>{yf_consensus}</td></tr>
                <tr><td><strong>YF Analyst Count</strong></td><td>{yf_analysts_count}</td></tr>
            </table>
            """, unsafe_allow_html=True)
   
    except Exception as e:
        st.error(f"Failed to fetch data. {str(e)}")

''
''
''

st.info('Data provided by Yahoo Finance')
