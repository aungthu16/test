import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Stock Data Web Scraping")

ticker = st.text_input("Enter your stock ticker:")

url = "https://stockanalysis.com/stocks/"+ticker+"/"
response = requests.get(url)

if st.button("Submit"):
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table1 = soup.find_all('table')[0]
    stock_data1 = {}
    if table1:  
          rows = table1.find_all('tr')
          for row in rows:
              cols = row.find_all('td')
              if len(cols) == 2:  
                  key = cols[0].text.strip()
                  value = cols[1].text.strip()
                  stock_data1[key] = value
          market_cap = stock_data1.get("Market Cap", "N/A")
          revenue_ttm = stock_data1.get("Revenue (ttm)", "N/A")
          net_income_ttm = stock_data1.get("Net Income (ttm)", "N/A")
          pe_ratio = stock_data1.get("PE Ratio", "N/A")
          dividend_yield = stock_data1.get("Dividend", "N/A")
          shares_outstanding = stock_data1.get("Shares Out", "N/A")
          eps = stock_data1.get("EPS (ttm)", "N/A")
          forward_pe = stock_data1.get("Forward PE", "N/A")
          ex_dividend_date = stock_data1.get("Ex-Dividend Date", "N/A")
          print(f"Market Cap: {market_cap}")
          print(f"Revenue (ttm): {revenue_ttm}")
          print(f"Net Income (ttm): {net_income_ttm}")
          print(f"P/E Ratio: {pe_ratio}")
          print(f"Dividend Yield: {dividend_yield}")
          print(f"Shares Outstanding: {shares_outstanding}")
          print(f"EPS (ttm): {eps}")
          print(f"Forward PE: {forward_pe}")
          print(f"Ex-Dividend Date: {ex_dividend_date}")

          st.subheader("Table 1: Stock Overview")
          st.write(f"Market Cap: {market_cap}")
          st.write(f"Revenue (ttm): {revenue_ttm}")
          st.write(f"Net Income (ttm): {net_income_ttm}")
          st.write(f"P/E Ratio: {pe_ratio}")
          st.write(f"Dividend Yield: {dividend_yield}")
          st.write(f"Shares Outstanding: {shares_outstanding}")
          st.write(f"EPS (ttm): {eps}")
          st.write(f"Forward PE: {forward_pe}")
          st.write(f"Ex-Dividend Date: {ex_dividend_date}")
    else:
          print("Table not found on the page")

    table2 = soup.find_all('table')[1]
    stock_data2 = {}
    if table2:
          rows = table2.find_all('tr')
          for row in rows:
              cols = row.find_all('td')
              if len(cols) == 2:  
                  key = cols[0].text.strip()
                  value = cols[1].text.strip()
                  stock_data2[key] = value
          volume = stock_data2.get("Volume", "N/A")
          open = stock_data2.get("Open", "N/A")
          previous_close = stock_data2.get("Previous Close", "N/A")
          day_range = stock_data2.get("Day's Range", "N/A")
          year_range = stock_data2.get("52-Week Range", "N/A")
          beta = stock_data2.get("Beta", "N/A")
          analysts = stock_data2.get("Analysts", "N/A")
          price_target = stock_data2.get("Price Target", "N/A")
          earnings_date = stock_data2.get("Earnings Date", "N/A")
          print(f"Volume: {volume}")
          print(f"Open: {open}")
          print(f"Previous Close: {previous_close}")
          print(f"Day's Range: {day_range}")
          print(f"52week Range: {year_range}")
          print(f"Beta: {beta}")
          print(f"SA Analysts: {analysts}")
          print(f"SA Price Target: {price_target}")
          print(f"Earnings Date: {earnings_date}")

          st.subheader("Table 2: Stock Overview")
          st.write(f"Volume: {volume}")
          st.write(f"Open: {open}")
          st.write(f"Previous Close: {previous_close}")
          st.write(f"Day's Range: {day_range}")
          st.write(f"52week Range: {year_range}")
          st.write(f"Beta: {beta}")
          st.write(f"SA Analysts: {analysts}")
          st.write(f"SA Price Target: {price_target}")
          st.write(f"Earnings Date: {earnings_date}")
    else:
          print("Table not found on the page")
  
  else:
      print("Failed to retrieve the webpage")

    
    
  