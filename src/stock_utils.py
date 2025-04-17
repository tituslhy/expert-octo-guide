#%%
import pandas as pd
import yfinance as yf

def get_stock_prices(
    ticker: str,
    period: str,
):
    """Function to get stock prices for a ticker of interest"""
    return rename_columns(
        ticker=ticker,
        df=yf.Ticker(ticker).history(period=period),
    )

def calculate_cagr(
    ticker: str,
    period: str,
):
    """Function to compute CAGR of a stock ticker of interest 
    across a time interval."""
    
    df = rename_columns(
        ticker=ticker,
        df=yf.Ticker(ticker).history(period=period),
    )
    df = df.sort_index()

    # Renamed column will be like "AAPL_close"
    close_col = f"{ticker}_close"

    if close_col not in df.columns:
        raise ValueError(f"Expected column '{close_col}' not found in DataFrame.")

    start_date, end_date = df.index[0], df.index[-1]
    start_price = df[close_col].iloc[0]
    end_price   = df[close_col].iloc[-1]

    # Compute approximate number of years accounting for leap years
    delta_days = (end_date - start_date).days
    years = delta_days / 365.25
    if years <= 0:
        raise ValueError("Time period must span more than 0 years.")

    cagr_value = (end_price / start_price)**(1/years) - 1
    return f"{round(100 * cagr_value, 1)}%"

def rename_columns(ticker: str, df: pd.DataFrame) -> pd.DataFrame:
    """Helper function to post-process dataframe column names"""
    column_dict = {old_name: process_string(ticker = ticker,
                                            string_ = old_name) \
        for old_name in df.columns.values.tolist()}
    df.rename(columns=column_dict, inplace=True)
    return df

def process_string(ticker: str, 
                    string_: str) -> str:
    """Utility function to process string names in the dataframe"""
    return f"{ticker}_{'_'.join(string_.lower().split(" "))}"
# %%
