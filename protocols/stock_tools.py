#%%
from fastmcp import FastMCP

from tqdm import tqdm
from typing import Dict, Any, Optional

import os
import sys

__curdir__ = os.getcwd()
if "mcp" in __curdir__:
    sys.path.append("../src")
else:
    sys.path.append("./src")

from stock_utils import get_stock_prices, calculate_cagr
from stock_models import TickerList, Interval

mcp = FastMCP(
    name="Stock Analysis Tool 📈",
    instructions="""This server provides tools to get stock prices and gets the compounded annual growth rate (CAGR) of tickers.
        Call `get_stock_price` to get the current price of a stock ticker, and `get_cagr` to calculate the CAGR 
        of a stock ticker of interest.""",
)

@mcp.resource(
    uri="data://app-status",
    name="ApplicationStatus",
    description="Provides current status of application.",
    mime_type="application/json",
    tags={"monitoring", "status"}
)
def get_application_status() -> Dict[str, Any]:
    """
    Internal function description ignored if description is provided above.
    """
    return {
        "status": "ok",
        "version": mcp.settings.version
    }

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
            data = get_stock_prices(ticker, period=ticker_list.period)
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
   return calculate_cagr(ticker=ticker, period=period)
#%%
if __name__ == "__main__":
    print("🚀Starting server... ")
    mcp.run(
        transport="sse"
    )