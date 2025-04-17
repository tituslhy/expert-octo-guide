import pandas as pd

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