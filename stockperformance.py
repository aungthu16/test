import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import math
import numpy
import http.client
import json
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='Stock Analysis Dashboard',
                   page_icon=':chart_with_upwards_trend:'
)

st.title("Stock Analysis Dashboard")
''
@st.cache_data
def get_stock_data(ticker, apiKey=None):

    performance_id = None
    fair_value = fvDate = moat = moatDate = starRating = assessment = 'N/A'
    if apiKey:
        try:
            conn = http.client.HTTPSConnection("morning-star.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "morning-star.p.rapidapi.com"
            }
            conn.request("GET", "/market/v2/auto-complete?q=" + ticker, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            for item in json_data.get('results', []):
                if item.get('ticker', '').upper() == ticker.upper():
                    performance_id = item.get('performanceId')
                    break
        except Exception as e:
            st.warning(f"API request failed: {e}")

    if performance_id:
        try:
            conn = http.client.HTTPSConnection("morning-star.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "morning-star.p.rapidapi.com"
            }
            conn.request("GET", "/stock/v2/get-analysis-data?performanceId="+ performance_id, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            fair_value = json_data['valuation']['fairValue']
            fvDate = json_data['valuation']['fairValueDate']
            moat = json_data['valuation']['moat']
            moatDate = json_data['valuation']['moatDate']
            starRating = json_data['valuation']['startRating']
            assessment = json_data['valuation']['assessment']
        except Exception as e:
            st.warning(f"data request failed: {e}")
    
    epsRevisionsGrade = dpsRevisionsGrade = dividendYieldGrade = divSafetyCategoryGrade = divGrowthCategoryGrade = divConsistencyCategoryGrade = sellSideRating = ticker_id = quant_rating = growth_grade = momentum_grade = profitability_grade = value_grade = yield_on_cost_grade = 'N/A'
    if apiKey:
        try:
            conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
            }
            conn.request("GET", "/symbols/get-ratings?symbol=" + ticker, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            first_data = json_data['data'][0]['attributes']['ratings']
            ticker_id = json_data['data'][0]['attributes']['tickerId']
            quant_rating = first_data['quantRating']
            growth_grade = first_data['growthGrade']
            momentum_grade = first_data['momentumGrade']
            profitability_grade = first_data['profitabilityGrade']
            value_grade = first_data['valueGrade']
            yield_on_cost_grade = first_data['yieldOnCostGrade']
            epsRevisionsGrade = first_data['epsRevisionsGrade']
            dpsRevisionsGrade = first_data['dpsRevisionsGrade']
            dividendYieldGrade = first_data['dividendYieldGrade']
            divSafetyCategoryGrade = first_data['divSafetyCategoryGrade']
            divGrowthCategoryGrade = first_data['divGrowthCategoryGrade']
            divConsistencyCategoryGrade = first_data['divConsistencyCategoryGrade']
            sellSideRating = first_data['sellSideRating']
        except Exception as e:
            st.warning(f"API request failed: {e}")
        
    sk_targetprice = 'N/A'
    if apiKey and ticker_id and ticker_id != 'N/A':
        ticker_id_str = str(ticker_id)
        try:
            conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
            }
            conn.request("GET", "/symbols/get-analyst-price-target?ticker_ids=" + ticker_id_str + "&return_window=1&group_by_month=false", headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            get_sk_data = json_data['estimates'][f'{ticker_id}']['target_price']['0'][0]
            sk_targetprice = get_sk_data['dataitemvalue']
        except Exception as e:
            st.warning(f"API request failed: {e}")

    lowercase_ticker = ticker.lower()
    picture_url = f'https://logos.stockanalysis.com/{lowercase_ticker}.svg'

    try:
        sa_statistics_url = f'https://stockanalysis.com/stocks/{ticker}/statistics/'
        sa_statistics_response = requests.get(sa_statistics_url)
        sa_statistics_soup = BeautifulSoup(sa_statistics_response.content, "html.parser")

        sa_analyst_table = sa_statistics_soup.find_all('table')[15]
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
    except Exception as e:
        st.warning(f"Failed to scrape data from StockAnalysis: {e}")

    stock = yf.Ticker(ticker)
    data = stock.history(period='max')

    if data.empty:
        raise ValueError("No data found for this ticker.")

    name = stock.info.get('longName', 'N/A')
    sector = stock.info.get('sector', 'N/A')
    industry = stock.info.get('industry', 'N/A')
    employee = stock.info.get('fullTimeEmployees', 'N/A')
    marketCap = stock.info.get('marketCap', 'N/A')
    price = stock.info.get('currentPrice', 'N/A')
    previous_close = data['Close'].iloc[-2]
    beta = stock.info.get('beta', 'N/A')
    longProfile = stock.info.get('longBusinessSummary', 'N/A')
    eps = stock.info.get('trailingEps', 'N/A')
    pegRatio = stock.info.get('pegRatio', 'N/A')
    country = stock.info.get('country', 'N/A')
    yf_targetprice = stock.info.get('targetMeanPrice', 'N/A')
    yf_consensus = stock.info.get('recommendationKey', 'N/A')
    yf_analysts_count = stock.info.get('numberOfAnalystOpinions', 'N/A')
    website = stock.info.get('website', 'N/A')
    peRatio = stock.info.get('trailingPE', 'N/A')
    forwardPe = stock.info.get('forwardPE', 'N/A')
    dividendYield = stock.info.get('dividendYield', 'N/A')
    payoutRatio = stock.info.get('payoutRatio', 'N/A')
    sharesOutstanding = stock.info.get('sharesOutstanding', 'N/A')
    try:
        totalEsg = stock.sustainability.loc['totalEsg', 'esgScores']
        enviScore = stock.sustainability.loc['environmentScore', 'esgScores']
        socialScore = stock.sustainability.loc['socialScore', 'esgScores']
        governScore = stock.sustainability.loc['governanceScore', 'esgScores']
        percentile = stock.sustainability.loc['percentile', 'esgScores']
        insiderPct = stock.major_holders.loc['insidersPercentHeld', 'Value']
        institutionsPct = stock.major_holders.loc['institutionsPercentHeld', 'Value']
    except (KeyError, AttributeError, IndexError) as e:
        totalEsg = enviScore = socialScore = governScore = percentile = insiderPct = institutionsPct = "N/A"

    change_dollar = price - previous_close
    change_percent = (change_dollar / previous_close) * 100

    yf_mos = ((yf_targetprice - price)/yf_targetprice) * 100
    sa_price_float = float(sa_analysts_targetprice.replace('$', ''))
    sa_mos = ((sa_price_float - price)/sa_price_float) * 100

    return assessment, sk_targetprice, quant_rating, growth_grade, momentum_grade, profitability_grade, value_grade, yield_on_cost_grade, sharesOutstanding, institutionsPct, insiderPct, totalEsg, enviScore, socialScore, governScore, percentile, price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website, peRatio, forwardPe, dividendYield, payoutRatio, performance_id, fair_value, fvDate, moat, moatDate, starRating, yf_mos, sa_mos

''
''

############### Inputs ###############

input_col1, input_col2 = st.columns([1, 3])
with input_col1:
    ticker = st.text_input("Enter US Stock Ticker:", "AAPL")
with input_col2:
    apiKey = st.text_input("Enter your RapidAPI Key (optional):", "")

st.info('Data provided by Yahoo Finance, Morning Star, and StockAnalysis.com')

if st.button("Submit"):
    try:
        assessment, sk_targetprice, quant_rating, growth_grade, momentum_grade, profitability_grade, value_grade, yield_on_cost_grade, sharesOutstanding, institutionsPct, insiderPct, totalEsg, enviScore, socialScore, governScore, percentile, price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website, peRatio, forwardPe, dividendYield, payoutRatio, performance_id, fair_value, fvDate, moat, moatDate, starRating, yf_mos, sa_mos = get_stock_data(ticker, apiKey if apiKey.strip() else None)
    
############### Profile ###############

        st.header(f'{name}', divider='gray')

        ''
        ''

        employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}'
        marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}'

        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"""
            <div style='text-align: left;'>
                <img src='{picture_url}' width='100'>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style='float: left; width: 100%;'>
                <table style='width: 100%;'>
                    <tr><td><strong>Sector</strong></td><td>{sector}</td></tr>
                    <tr><td><strong>Industry</strong></td><td>{industry}</td></tr>
                    <tr><td><strong>Employees</strong></td><td>{employee_value}</td></tr>
                    <tr><td><strong>Market Cap</strong></td><td>{marketCap_value}</td></tr>
                    <tr><td><strong>Country</strong></td><td>{country}</td></tr>
                    <tr><td><strong>Website</strong></td><td>{website}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        h_cols = st.columns(3)
        sharesOutstanding_value = 'N/A' if sharesOutstanding == 'N/A' else f'{sharesOutstanding/1000000000:,.2f}B'
        h_cols[0].metric(
            label='Shares Outstanding',
            value=sharesOutstanding_value
        )
        insiderPct_value = 'N/A' if insiderPct == 'N/A' else f'{insiderPct*100:,.2f}%'
        h_cols[1].metric(
            label='Owned by Insiders',
            value=insiderPct_value
        )
        institutionsPct_value = 'N/A' if institutionsPct == 'N/A' else f'{institutionsPct*100:,.2f}%'
        h_cols[2].metric(
            label='Owned by Institutions',
            value=institutionsPct_value
        )

        st.markdown(f"<div style='text-align: justify;'>{longProfile}</div>", unsafe_allow_html=True)

        ''
        ''

############### Tabs ###############

        overview_data, comparison_data, statements_data, sustainability_data, news_data, technicalAnalysis_data = st.tabs (["Overview","Comparisons","Statement","Sustainability","Top 10 news", "Technical Analysis"])

############### Overview Data ###############

        with overview_data:

            #Stock Performance
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

            cols1 = st.columns(4)
            pe_value = 'N/A' if peRatio == 'N/A' else f'{peRatio:.2f}'
            cols1[0].metric(
                label='PE Ratio',
                value=pe_value
            )
            forwardPe_value = 'N/A' if forwardPe == 'N/A' else f'{forwardPe:.2f}'
            cols1[1].metric(
                label='Forward PE',
                value=forwardPe_value
            )
            dividendyield_value = 'N/A' if dividendYield == 'N/A' else f'{dividendYield*100:.2f}%'
            cols1[2].metric(
                label='Dividend Yield',
                value=dividendyield_value
            )
            payoutRatio_value = 'N/A' if payoutRatio == 'N/A' else f'{payoutRatio:.2f}'
            cols1[3].metric(
                label='Payout Ratio',
                value=payoutRatio_value
            )
            ''

            #Morning Star Research
            st.subheader('Morningstar Research', divider='gray')
            st.caption("This section only works with RapidAPI key.")
            starRating_value = 0 if starRating == 'N/A' else int(starRating)
            star_rating = ":star:" * int(round(starRating_value, 0))
            column1, column2, column3 = st.columns(3)
            with column1:
                st.write("Economic Moat")
                st.subheader(f'{moat}')
            fair_value_mos = 'N/A' if fair_value == 'N/A' else f'{((float(fair_value) - price)/float(fair_value)) * 100:.2f}%'
            fair_value_fix = 'N/A' if fair_value == 'N/A' else f'${float(fair_value):.2f}'
            with column2:
                st.write("Fair Value")
                st.subheader(f'{fair_value_fix}')  
                if fair_value != 'N/A':  
                    mos_value = ((float(fair_value) - price)/float(fair_value)) * 100
                    if mos_value < 0:
                        st.markdown(f'<p style="color:red;">{fair_value_mos}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p style="color:green;">{fair_value_mos}</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:gray;">N/A</p>', unsafe_allow_html=True)  
            with column3:
                st.write("Rating")
                st.subheader(f'{star_rating}')
            ''
            st.markdown(f'The stock is currently <span style="color:blue;">{assessment}</span>.', unsafe_allow_html=True)
            ''
            st.caption(f"An economic moat refers to a company's ability to maintain competitive advantages to protect its long-term profits and market share from competitors.<br>Moat Assessment Date: {moatDate}", unsafe_allow_html=True)
            ''
            st.caption(f"The Star Rating is determined by three factors: a stock's current price, Morningstar's estimate of the stock's fair value, and the uncertainty rating of the fair value. The bigger the discount, the higher the star rating. Four- and 5-star ratings mean the stock is undervalued, while a 3-star rating means it's fairly valued, and 1- and 2-star stocks are overvalued. When looking for investments, a 5-star stock is generally a better opportunity than a 1-star stock.<br>Fair Value Assessment Date: {fvDate}", unsafe_allow_html=True)
            ''

            #Quant Rating
            st.subheader('Quantitative Analysis [Seeking Alpha]', divider = 'gray')
            st.caption("This section only works with RapidAPI key.")
            st.write(quant_rating)
            st.write(growth_grade)
            st.write(momentum_grade)
            st.write(profitability_grade)
            st.write(value_grade)
            st.write(yield_on_cost_grade)
            ''

            #Analysts Ratings
            st.subheader('Analysts Ratings', divider='gray')
            col1, col2, col3 = st.columns([3, 3, 3])
            yf_targetprice_value = 'N/A' if yf_targetprice == 'N/A' else f'${yf_targetprice}'
            yf_mos_value = 'N/A' if yf_mos == 'N/A' else f'{yf_mos:.2f}%'
            with col1:
                st.markdown(''':violet-background[Yahoo Finance]''')
                st.write(f'Price Target: {yf_targetprice_value}')
                st.write(f'Difference %: {yf_mos_value}')
                st.write(f'Analyst Consensus: {yf_consensus}')
                st.write(f'Analyst Count: {yf_analysts_count}')
            
            sk_targetprice_fix = 'N/A' if sk_targetprice == 'N/A' else f'${float(sk_targetprice):.2f}'
            sk_targetprice_mos ='N/A' if sk_targetprice =='N/A' else f'{((float(sk_targetprice) - price)/float(sk_targetprice)) * 100:.2f}%'
            with col2:
                st.markdown(''':orange-background[Seeking Alpha]''')
                st.write(f'Price Target: {sk_targetprice_fix}')
                st.write(f'Difference %: {sk_targetprice_mos}')

            sa_mos_value = 'N/A' if sa_mos == 'N/A' else f'{sa_mos:.2f}%'
            with col3:
                st.markdown(''':blue-background[Stockanalysis.com]''')
                st.write(f'Price Target: {sa_analysts_targetprice}')
                st.write(f'Difference %: {sa_mos_value}')
                st.write(f'Analyst Consensus: {sa_analysts_consensus}')
                st.write(f'Analyst Count: {sa_analysts_count}')

            ''

############### Statements ###############

        with comparison_data:
            st.write("Comparisons")

############### Statements ###############

        with statements_data:
            st.write("Statements")

############### Technical Analysis Data ###############

        with technicalAnalysis_data:
            st.subheader("Price Data", divider ='gray')
            """
            col1, col2 = st.columns([3, 3])
            with col1:    
                start_date = st.date_input('Start Date')
            with col2:
                end_date = st.date_input('End date')
            data = yf.download(ticker, start=start_date,end=end_date)
            fig = px.line(data, x = data.index, y=data['Adj close'],title = ticker)
            st.plotly_chart(fig) 
            """
            #df = pd.DataFrame()
            #ind_list = df.ta.indicators(as_list=True)
            #st.write(ind_list)
        
############### Sustainability Data ###############

        with sustainability_data:
            st.subheader("Sustainability", divider = 'gray')
            #st.caption("This section shows the ESG risk ratings of '" + name + "' .")

            #Gauge Plot
            def plot_gauge():
                totalEsg_value = 0.00 if totalEsg == 'N/A' else totalEsg
                max_value = 100
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=totalEsg_value,
                    title={'text': "Total ESG Risk"},
                    gauge={
                        'axis': {'range': [None, max_value]},
                        'bar': {'color': "blue"},
                        'steps': [
                            {'range': [0, max_value * 0.25], 'color': "lightgray"},
                            {'range': [max_value * 0.25, max_value * 0.5], 'color': "yellow"},
                            {'range': [max_value * 0.5, max_value * 0.75], 'color': "orange"},
                            {'range': [max_value * 0.75, max_value], 'color': "red"},
                        ],
                    }
                ))
                gauge.update_layout(
                    autosize=False,
                    width=300,  
                    height=200, 
                    margin={'l': 50, 'r': 50, 't': 10, 'b': 0} 
                )
                st.plotly_chart(gauge)
            left_column, middle_column, right_column = st.columns([1, 3, 1])
            with middle_column:
                plot_gauge()
            
            #Risk Scores
            esgcol1 = st.columns(3)
            esgcol1[0].metric(
                label='Environmental Risk',
                value=enviScore
            )
            esgcol1[1].metric(
                label='Social Risk',
                value=socialScore
            )
            esgcol1[2].metric(
                label='Governance Risk',
                value=governScore
            )

            #Descriptions
            st.caption("Notes:")
            st.write("Total ESG Risk: Companies with ESG scores closer to 100 are considered to have significant ESG-related risks and challenges that could potentially harm their long-term sustainability.")
            st.write("Environmental Risk: This reflects the company’s impact on the environment. e.g. carbon emissions, waste management, energy efficiency.")
            st.write("Social Risk: This measures the company’s relationships with employees, suppliers, customers, and the community. e.g. human rights, labor practices, diversity, and community engagement.")
            st.write("Governance Risk: this focuses on the company’s leadership, audit practices, internal controls, and shareholder rights. e.g. transparent financial reporting and strong board oversight.")

############### News Data ###############

        with news_data:
            st.subheader("News", divider = 'gray')
            st.write(f'{name}')
            st.write(f'{ticker}')
            ''

    except Exception as e:
        st.error(f"Failed to fetch data. {str(e)}")

''
''
''
