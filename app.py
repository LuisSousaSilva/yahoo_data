import streamlit as st
import yfinance as yf
import pandas as pd

def download_adjusted_data(tickers, start_date, end_date):
    # Download data
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        group_by='ticker',
        auto_adjust=False,
        threads=True
    )

    adjusted_data = []

    for ticker in tickers:
        # Handle single and multiple tickers
        if len(tickers) == 1:
            df = data.copy()
        else:
            df = data[ticker].copy()

        df.dropna(inplace=True)
        df.reset_index(inplace=True)

        # Calculate adjustment factor
        df['Adj Factor'] = df['Adj Close'] / df['Close']

        # Adjust prices
        df['Open_adj'] = df['Open'] * df['Adj Factor']
        df['High_adj'] = df['High'] * df['Adj Factor']
        df['Low_adj'] = df['Low'] * df['Adj Factor']
        df['Close_adj'] = df['Adj Close']  # Already adjusted

        # Prepare output format
        df['TICKER'] = ticker
        df['PER'] = 'D'
        df['DTYYYYMMDD'] = df['Date'].dt.strftime('%Y%m%d')
        df['VOL'] = df['Volume']

        # Select and rename columns
        df_output = df[['TICKER', 'PER', 'DTYYYYMMDD', 'Open_adj', 'High_adj', 'Low_adj', 'Close_adj', 'VOL']]
        df_output.columns = ['<TICKER>', '<PER>', '<DTYYYYMMDD>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']

        adjusted_data.append(df_output)

    # Concatenate data from all tickers
    result = pd.concat(adjusted_data)

    # Round to 4 decimal places
    result = round(result, 4)

    return result

# Streamlit App
st.title('Yahoo Finance Adjusted Data Downloader')

# User Inputs
tickers_input = st.text_input('Enter ticker symbols separated by commas (e.g., AAPL, MSFT, BTC-USD):')
start_date = st.date_input('Start Date')
end_date = st.date_input('End Date')

if st.button('Download Data'):
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]
    if not tickers:
        st.error('Please enter at least one ticker symbol.')
    else:
        # Download and adjust data
        with st.spinner('Downloading and processing data...'):
            df = download_adjusted_data(tickers, start_date, end_date)
        st.success('Data downloaded and adjusted successfully!')

        # Display Data
        st.dataframe(df)

        # Download Link
        csv = df.to_csv(index=False)
        st.download_button(
            label='Download CSV',
            data=csv,
            file_name='data.csv',
            mime='text/csv'
        )
