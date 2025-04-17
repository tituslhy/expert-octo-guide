#%%
from fastmcp import FastMCP

from tqdm import tqdm
from typing import Dict, Any, Optional
import yfinance as yf

import sys
sys.path.append("./")
from utils import rename_columns
from models import TickerList, Interval

mcp = FastMCP(
    name="Stock Analysis Tool 📈",
    instructions="""This server provides tools to get stock prices and gets the compounded annual growth rate (CAGR) of tickers.
        Call `get_stock_price` to get the current price of a stock ticker, and `get_cagr` to calculate the CAGR 
        of a stock ticker of interest.""",
    port=3000,
)

@mcp.tool()
def get_stock_price(
    ticker_list: TickerList,
) -> Dict[str, Any]:
    """Gets stock prices for tickers of interest.
    
    Args:
        ticker_list (TickerList): A TickerList schema containing the
        stock tickers of interest and the price period of interest.
    """
    prices = dict()
    for ticker in tqdm(ticker_list.tickers, desc="Fetching stock prices"):
        try:
            data = rename_columns(ticker = ticker, df = yf.Ticker(ticker).history(period=ticker_list.period))
            prices[f'{ticker}_price'] = data.to_dict(orient='records')
        except Exception as e:
            prices[ticker] = str(e)
    return prices

@mcp.tool(
    name="get_cagr",
    description="Computes the compounded annual growth rate (CAGR) of a stock ticker of interest.",
    tags={"cagr", "data_analysis"}
)
def cagr(
    ticker: str,
    period: Optional[Interval] = "10y"    
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
#%%
if __name__ == "__main__":
    print("🚀Starting server... ")
    mcp.run(
        transport="sse"
    )