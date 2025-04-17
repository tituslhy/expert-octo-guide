from pydantic import BaseModel, Field
from typing import List, Literal, Optional, TypeAlias

Interval: TypeAlias = Literal["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]

class TickerList(BaseModel):
    tickers: List[str] = Field(..., description="A list of stock tickers of interest")
    period: Optional[Interval] = Field(
        default="1mo",
        description="Time period for data retrieval. Defaults to '1mo'."
    )