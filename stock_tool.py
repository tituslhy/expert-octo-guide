from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from tqdm import tqdm

import yfinance as yf

mcp = FastMCP(
    name="Stock Analysis Tool 📈",
    instructions=(
        "This server provides tools to get stock prices and gets the compounded annual growth rate (CAGR) of tickers. ",
        "Call `get_stock_price` to get the current price of a stock ticker, and `get_cagr` to calculate the CAGR ",
        "of a stock ticker of interest."
    )
)

class TickerList(BaseModel):
    tickers: List[str] = Field(..., description="A list of stock tickers of interest")
    period: Optional[Literal[
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max"]
    ] = "1mo"

@mcp.tool()
def get_stock_ticker(
    ticker_list: TickerList,
) -> Dict[str, Any]:
    """Gets stock prices for tickers of interest."""
    prices = dict()
    # Get the stock prices for the tickers of interest
    for ticker in tqdm(ticker_list.tickers, desc="Fetching stock prices"):
        try:
            data = yf.Ticker(ticker).history(period=ticker_list.period)
            prices[f'{ticker}_price'] = data.to_dict(orient='records')
        except Exception as e:
            prices[ticker] = str(e)
    return prices

