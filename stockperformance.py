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
import altair as alt
import datetime

st.set_page_config(page_title='Stock Analysis Dashboard'
)

st.title("Stock Analysis Dashboard")

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
    
    authors_strongsell_count = authors_strongbuy_count = authors_sell_count = authors_hold_count = authors_buy_count = authors_rating = authors_count = epsRevisionsGrade = dpsRevisionsGrade = dividendYieldGrade = divSafetyCategoryGrade = divGrowthCategoryGrade = divConsistencyCategoryGrade = sellSideRating = ticker_id = quant_rating = growth_grade = momentum_grade = profitability_grade = value_grade = yield_on_cost_grade = 'N/A'
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
            #
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
            #
            authors_count = first_data['authorsCount']
            authors_rating = first_data['authorsRating']
            authors_buy_count = first_data['authorsRatingBuyCount']
            authors_hold_count = first_data['authorsRatingHoldCount']
            authors_sell_count = first_data['authorsRatingSellCount']
            authors_strongbuy_count = first_data['authorsRatingStrongBuyCount']
            authors_strongsell_count = first_data['authorsRatingStrongSellCount']

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
    pbRatio = stock.info.get('priceToBook','N/A')
    deRatio = stock.info.get('debtToEquity','N/A')
    dividends = stock.info.get('dividendRate','N/A')
    dividend_history = stock.dividends
    exDividendDate = stock.info.get('exDividendDate','N/A')
    get_earningsDate = stock.calendar['Earnings Date']
    earnings_history = stock.earnings_history
    eps_trend = stock.eps_trend
    if get_earningsDate:
        earningsDate = get_earningsDate[0].strftime('%Y-%m-%d')
    else:
        earningsDate = 'N/A'
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

    return eps_trend, earnings_history, earningsDate, exDividendDate, dividend_history, pbRatio, deRatio, dividends, ticker, authors_strongsell_count, authors_strongbuy_count, authors_sell_count, authors_hold_count, authors_buy_count, authors_rating, authors_count, assessment, sk_targetprice, quant_rating, growth_grade, momentum_grade, profitability_grade, value_grade, yield_on_cost_grade, sharesOutstanding, institutionsPct, insiderPct, totalEsg, enviScore, socialScore, governScore, percentile, price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website, peRatio, forwardPe, dividendYield, payoutRatio, performance_id, fair_value, fvDate, moat, moatDate, starRating, yf_mos, sa_mos, apiKey

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
        eps_trend, earnings_history, earningsDate, exDividendDate, dividend_history, pbRatio, deRatio, dividends, ticker, authors_strongsell_count, authors_strongbuy_count, authors_sell_count, authors_hold_count, authors_buy_count, authors_rating, authors_count, assessment, sk_targetprice, quant_rating, growth_grade, momentum_grade, profitability_grade, value_grade, yield_on_cost_grade, sharesOutstanding, institutionsPct, insiderPct, totalEsg, enviScore, socialScore, governScore, percentile, price, change_percent, change_dollar, beta, name, sector, industry, employee, marketCap, longProfile, eps, pegRatio, picture_url, country, sa_analysts_consensus, sa_analysts_targetprice, sa_analysts_count, yf_targetprice, yf_consensus, yf_analysts_count, website, peRatio, forwardPe, dividendYield, payoutRatio, performance_id, fair_value, fvDate, moat, moatDate, starRating, yf_mos, sa_mos, apiKey = get_stock_data(ticker, apiKey if apiKey.strip() else None)
    
############### Profile ###############

        st.header(f'{name}', divider='gray')
        ''
        ''
        employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}'
        marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}'
        col1, col2 = st.columns([2, 3])
        with col1:
            st.image(picture_url, use_column_width=True)
            # st.markdown(f"""
            # <div style='text-align: left;'>
            #     <img src='{picture_url}' width='100'>
            # </div>
            # """, unsafe_allow_html=True)
        with col2:
             st.markdown(f"""
             <div style='float: left; width: 100%;'>
                 <table style='width: 100%;'>
                     <tr><td><strong>Sector</strong></td><td>{sector}</td></tr>
                     <tr><td><strong>Industry</strong></td><td>{industry}</td></tr>
                     <tr><td><strong>Employees</strong></td><td>{employee_value}</td></tr>
                     <tr><td><strong>Market Cap</strong></td><td>{marketCap_value} Millions</td></tr>
                     <tr><td><strong>Country</strong></td><td>{country}</td></tr>
                     <tr><td><strong>Website</strong></td><td>{website}</td></tr>
                     <tr><td><strong>Earnings Date</strong></td><td>{earningsDate}</td></tr>
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

        overview_data, comparison_data, statements_data, sustainability_data, news_data, technicalAnalysis_data = st.tabs (["Overview","Comparisons","Financial Statements","Sustainability","Top 10 news","Technical Analysis"])

############### Overview Data ###############

        with overview_data:

#Stock Performance
            st.subheader('Stock Performance', divider='gray')
            cols = st.columns(4)
            cols[0].metric(
                label='Current Price',
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
            pbRatio_value = 'N/A' if pbRatio == 'N/A' else f'{pbRatio:.2f}'
            cols1[2].metric(
                label='PB Ratio',
                value=pbRatio_value
            )
            deRatio_value = 'N/A' if deRatio == 'N/A' else f'{deRatio/100:.2f}'
            cols1[3].metric(
                label='DE Ratio',
                value=deRatio_value
            )
            ''
            if apiKey is None:
                #st.markdown("---")
                st.warning('Certain information will be hidden due to unavailability of API key. Please input your API key to access the full data.')
                #st.markdown("---")
            else:
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
                #st.markdown(f'Current price of the stock is <span style="color:blue;">{assessment}</span>.', unsafe_allow_html=True)
                st.write(f'Morningstar Current Assessment: {assessment}')
                ''
                st.caption(f"An economic moat refers to a company's ability to maintain competitive advantages to protect its long-term profits and market share from competitors.<br>Moat Assessment Date: {moatDate}", unsafe_allow_html=True)
                st.caption(f"The Star Rating is determined by three factors: a stock's current price, Morningstar's estimate of the stock's fair value, and the uncertainty rating of the fair value. The bigger the discount, the higher the star rating. Four- and 5-star ratings mean the stock is undervalued, while a 3-star rating means it's fairly valued, and 1- and 2-star stocks are overvalued. When looking for investments, a 5-star stock is generally a better opportunity than a 1-star stock.<br>Fair Value Assessment Date: {fvDate}", unsafe_allow_html=True)
                ''

#Quant Rating
                st.subheader('Seeking Alpha Quantitative Analysis', divider = 'gray')
                st.caption("This section only works with RapidAPI key.")
                cols = st.columns(3)
                quant_rating_value = 'N/A' if quant_rating == 'N/A' else f'{quant_rating:.2f}'
                cols[0].metric(
                    label='Quant Rating',
                    value=quant_rating_value
                )
                cols[1].metric(
                    label='Growth Grade',
                    value=growth_grade
                )
                cols[2].metric(
                    label='Momentum Grade',
                    value=momentum_grade
                )

                cols = st.columns(3)
                cols[0].metric(
                    label='Profitability Grade',
                    value=profitability_grade
                )
                cols[1].metric(
                    label='Value Grade',
                    value=value_grade
                )
                cols[2].metric(
                    label='Yield on Cost Grade',
                    value=yield_on_cost_grade
                )
                ''

#Dividend data
            st.subheader('Dividends & Yields', divider='gray')
            if dividendYield == 'N/A':
                st.write(f'{name} has no dividend data.')
            else:
                col1, col2 = st.columns([1, 3])
                with col1:
                    dividends_value = 'N/A' if dividends == 'N/A' else f'${dividends:,.2f}'
                    st.metric(
                        label='Dividend per share',
                        value=dividends_value
                    )
                    dividendYield_value = 'N/A' if dividendYield == 'N/A' else f'{dividendYield*100:.2f}%'
                    st.metric(
                        label='Dividend Yield',
                        value=dividendYield_value
                    )
                    payoutRatio_value = 'N/A' if payoutRatio == 'N/A' else f'{payoutRatio:.2f}'
                    st.metric(
                        label='Payout Ratio',
                        value=payoutRatio_value
                    )
                    if exDividendDate == 'N/A':
                        exDividendDate_value = 'N/A'
                    else:
                        exDate = datetime.datetime.fromtimestamp(exDividendDate)
                        exDividendDate_value = exDate.strftime('%Y-%m-%d')
                    st.metric(
                        label='Ex-Dividend Date',
                        value=exDividendDate_value
                    )
                with col2:
                    data_yearly = dividend_history.resample('Y').sum().reset_index()
                    data_yearly['Year'] = data_yearly['Date'].dt.year
                    data_yearly = data_yearly[['Year', 'Dividends']]
                    if dividends != 'N/A':
                        data_yearly.loc[data_yearly.index[-1], 'Dividends'] = dividends
                    chart = alt.Chart(data_yearly).mark_bar().encode(
                        x=alt.X('Year:O', title='Year'), 
                        y=alt.Y('Dividends', title='Dividends (USD)'),
                        tooltip=['Year:O', 'Dividends']
                    ).properties(
                        title='Dividends History'
                    )
                    st.altair_chart(chart, use_container_width=True)

#Earnings History
            st.subheader('Earnings History', divider='gray')
            ecol1, ecol2 = st.columns([2, 3])
            with ecol1:
                earnings_data = pd.DataFrame(earnings_history)
                if 'epsEstimate' in earnings_data.columns and 'epsActual' in earnings_data.columns:
                    earnings_data.index = earnings_data.index.astype(str)
                    df = earnings_data.reset_index().melt(id_vars=['index'], value_vars=['epsEstimate', 'epsActual'], var_name='variable', value_name='value')
                    bar = alt.Chart(df[df['variable'] == 'epsActual']).mark_bar().encode(
                        x=alt.X('index:O', title='Date'),
                        y=alt.Y('value:Q', title='Actual')
                    ).properties(
                        width=alt.Step(40)
                    )
                    tick = alt.Chart(df[df['variable'] == 'epsEstimate']).mark_tick(
                        color='red',
                        thickness=2,
                        size=40 * 0.9,
                    ).encode(
                        x=alt.X('index:O', title='Date'),
                        y=alt.Y('value:Q', title='Estimate')
                    )
                    st.altair_chart(bar + tick)
                else:
                    st.write("The 'epsEstimate' or 'epsActual' columns are missing from the data.")
            with ecol2:
                eps_data = eps_trend.loc[["0y", "+1y"], ["current", "7daysAgo", "30daysAgo", "60daysAgo", "90daysAgo"]]
                eps_data = eps_data.T.reset_index()
                eps_data.columns = ['TimePeriod', 'CurrentYear', 'NextYear']
                label_map = {
                    'current': 'Current',
                    '7daysAgo': '7 Days Ago',
                    '30daysAgo': '30 Days Ago',
                    '60daysAgo': '60 Days Ago',
                    '90daysAgo': '90 Days Ago'
                }
                eps_data['TimePeriod'] = eps_data['TimePeriod'].map(label_map)
                eps_melted = pd.melt(eps_data, id_vars=['TimePeriod'], value_vars=['CurrentYear', 'NextYear'],
                                    var_name='Year', value_name='EPS')
                chart = alt.Chart(eps_melted).mark_line(point=True).encode(
                    x=alt.X('TimePeriod:N', title='Time Period', sort=['90 Days Ago', '60 Days Ago', '30 Days Ago', '7 Days Ago', 'Current']),
                    y=alt.Y('EPS:Q', title='EPS'),
                    color='Year:N',
                    tooltip=['TimePeriod', 'Year', 'EPS']
                ).properties(
                    title='EPS Trend'
                ).configure_axisX(
                labelAngle=-0
                )
                st.altair_chart(chart, use_container_width=True)

#Analysts Ratings
            st.subheader('Analysts Ratings', divider='gray')
            try:
                counts = {
                'Buy': authors_buy_count,
                'Sell': authors_sell_count,
                'Hold': authors_hold_count,
                'Strong Buy': authors_strongbuy_count,
                'Strong Sell': authors_strongsell_count
                }
                largest_count_type = max(counts, key=counts.get)
                largest_value = round(counts[largest_count_type])
            except Exception as e:
                largest_count_type = 'N/A'
                largest_value = 'N/A'
            col1, col2, col3 = st.columns([3, 3, 3])
            yf_targetprice_value = 'N/A' if yf_targetprice == 'N/A' else f'${yf_targetprice}'
            yf_mos_value = 'N/A' if yf_mos == 'N/A' else f'{yf_mos:.2f}%'
            with col1:
                st.markdown(''':violet-background[Yahoo Finance]''')
                st.write(f'Price Target: {yf_targetprice_value}')
                st.write(f'% Difference: {yf_mos_value}')
                st.write(f'Analyst Consensus: {yf_consensus}')
                st.write(f'Analyst Count: {yf_analysts_count}')
            
            sk_targetprice_fix = 'N/A' if sk_targetprice == 'N/A' else f'${float(sk_targetprice):.2f}'
            sk_targetprice_mos ='N/A' if sk_targetprice =='N/A' else f'{((float(sk_targetprice) - price)/float(sk_targetprice)) * 100:.2f}%'
            with col2:
                st.markdown(''':orange-background[Seeking Alpha]''')
                st.write(f'Price Target: {sk_targetprice_fix}')
                st.write(f'% Difference: {sk_targetprice_mos}')
                st.write(f'Analyst Consensus: {largest_count_type}')
                st.write(f'Analyst Count: {largest_value}')

            sa_mos_value = 'N/A' if sa_mos == 'N/A' else f'{sa_mos:.2f}%'
            with col3:
                st.markdown(''':blue-background[Stockanalysis.com]''')
                st.write(f'Price Target: {sa_analysts_targetprice}')
                st.write(f'% Difference: {sa_mos_value}')
                st.write(f'Analyst Consensus: {sa_analysts_consensus}')
                st.write(f'Analyst Count: {sa_analysts_count}')
            ''

############### Comparison ###############

        with comparison_data:
            st.write("Comparisons")

############### Statements ###############

        with statements_data:
            tickerdataframe = yf.Ticker(ticker)
#Income Statement
            income_statement = tickerdataframe.income_stmt
            quarterly_income_statement = tickerdataframe.quarterly_income_stmt
            st.subheader("Income Statement", divider ='gray')
            ttm = quarterly_income_statement.iloc[:, :4].sum(axis=1)
            income_statement.insert(0, 'TTM', ttm)
            income_statement_flipped = income_statement.iloc[::-1]
            formatted_columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in income_statement_flipped.columns]
            income_statement_flipped.columns = formatted_columns
            st.dataframe(income_statement_flipped)
            ''
#Income Statement Bar chart
            #st.subheader("Income Statement Key Values Chart", divider ='gray')
            income_items = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'EBITDA']
            income_bar_data = income_statement_flipped.loc[income_items].transpose()
            income_bar_data_million = income_bar_data / 1e6
            income_bar_data_million = income_bar_data_million.reset_index().rename(columns={'index': 'Date'})
            income_bar_data_melted = income_bar_data_million.melt('Date', var_name='Key Values', value_name='USD in Million')
            income_bar_data_melted['Key Values'] = pd.Categorical(income_bar_data_melted['Key Values'], categories=income_items, ordered=True)
            chart = alt.Chart(income_bar_data_melted).mark_bar().encode(
                x=alt.X('Date:O', title='Date'),
                y=alt.Y('USD in Million:Q', title='USD in Million'),
                color=alt.Color('Key Values:N', sort=income_items), 
                xOffset=alt.XOffset('Key Values:N', sort=income_items)
            ).properties(
                #width=600,
                #height=400,
                title='Income Statement Key Values Chart'
            ).configure_axisX(
                labelAngle=-45
            )
            st.altair_chart(chart, use_container_width=True)
            ''
#Balance Sheet
            balance_sheet = tickerdataframe.balance_sheet
            quarterly_balance_sheet = tickerdataframe.quarterly_balance_sheet
            st.subheader("Balance Sheet", divider ='gray')
            ttm = quarterly_balance_sheet.iloc[:, :4].sum(axis=1)
            balance_sheet.insert(0, 'TTM', ttm)
            balance_sheet_flipped = balance_sheet.iloc[::-1]
            formatted_columns2 = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in balance_sheet_flipped.columns]
            balance_sheet_flipped.columns = formatted_columns2
            st.dataframe(balance_sheet_flipped)
            ''
#Balance Sheet Bar chart
            #st.subheader("Balance Sheet Key Values Chart", divider ='gray')
            balance_items = ['Cash And Cash Equivalents','Total Assets', 'Total Liabilities Net Minority Interest', 'Stockholders Equity']
            balance_bar_data = balance_sheet_flipped.loc[balance_items].transpose()
            balance_bar_data_million = balance_bar_data / 1e6
            balance_bar_data_million = balance_bar_data_million.reset_index().rename(columns={'index': 'Date'})
            balance_bar_data_melted = balance_bar_data_million.melt('Date', var_name='Key Values', value_name='USD in Million')
            balance_bar_data_melted['Key Values'] = pd.Categorical(balance_bar_data_melted['Key Values'], categories=balance_items, ordered=True)
            chart2 = alt.Chart(balance_bar_data_melted).mark_bar().encode(
                x=alt.X('Date:O', title='Date'),
                y=alt.Y('USD in Million:Q', title='USD in Million'),
                color=alt.Color('Key Values:N', sort=balance_items), 
                xOffset=alt.XOffset('Key Values:N', sort=balance_items)
            ).properties(
                #width=600,
                #height=400,
                title='Balance Sheet Key Values Chart'
            ).configure_axisX(
                labelAngle=-45
            )
            st.altair_chart(chart2, use_container_width=True)
            ''
#Cashflow Statement
            cashflow_statement = tickerdataframe.cashflow
            quarterly_cashflow_statement = tickerdataframe.quarterly_cashflow
            st.subheader("Cashflow Statement", divider ='gray')
            ttm = quarterly_cashflow_statement.iloc[:, :4].sum(axis=1)
            cashflow_statement.insert(0, 'TTM', ttm)
            cashflow_statement_flipped = cashflow_statement.iloc[::-1]
            formatted_columns3 = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in cashflow_statement_flipped.columns]
            cashflow_statement_flipped.columns = formatted_columns3
            st.dataframe(cashflow_statement_flipped)
            ''
#Cashflow Statement Bar chart
            #st.subheader("Cashflow Statement Key Values Chart", divider ='gray')
            cashflow_items = ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow', 'Free Cash Flow']
            cashflow_bar_data = cashflow_statement_flipped.loc[cashflow_items].transpose()
            cashflow_bar_data_million = cashflow_bar_data / 1e6
            cashflow_bar_data_million = cashflow_bar_data_million.reset_index().rename(columns={'index': 'Date'})
            cashflow_bar_data_melted = cashflow_bar_data_million.melt('Date', var_name='Key Values', value_name='USD in Million')
            cashflow_bar_data_melted['Key Values'] = pd.Categorical(cashflow_bar_data_melted['Key Values'], categories=cashflow_items, ordered=True)
            chart = alt.Chart(cashflow_bar_data_melted).mark_bar().encode(
                x=alt.X('Date:O', title='Date'),
                y=alt.Y('USD in Million:Q', title='USD in Million'),
                color=alt.Color('Key Values:N', sort=cashflow_items), 
                xOffset=alt.XOffset('Key Values:N', sort=cashflow_items)
            ).properties(
                #width=600,
                #height=400,
                title='Cashflow Statement Key Values Chart'
            ).configure_axisX(
                labelAngle=-45
            )
            st.altair_chart(chart, use_container_width=True)
            ''

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
            ''
#Descriptions
            st.caption("Notes:")
            ''
            st.caption("Total ESG Risk: Companies with ESG scores closer to 100 are considered to have significant ESG-related risks and challenges that could potentially harm their long-term sustainability.")
            st.caption("Environmental Risk: This reflects the company’s impact on the environment. e.g. carbon emissions, waste management, energy efficiency.")
            st.caption("Social Risk: This measures the company’s relationships with employees, suppliers, customers, and the community. e.g. human rights, labor practices, diversity, and community engagement.")
            st.caption("Governance Risk: this focuses on the company’s leadership, audit practices, internal controls, and shareholder rights. e.g. transparent financial reporting and strong board oversight.")

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
