import pandas as pd

def get_quality_metrics(df : pd.DataFrame) -> None:
    """
    Quick check to see if extraction was successful. Reasons may need clarification by manual checks.
    Note:
    notice parsing may fail entirely if the site did not load, was not provided because of too many requests (Error 503)
    result parsing may fail if: 1. result is not on the page 2. result is in text form not in the relevant section 
    additional info may include details about the result, such as the value of the contract

    params:
    df: a dataset which has already been parsed from html and sectioned into parts like Buyer, Procedure, Results_long 
    """
    missing_notices = df[df["Notice"] == "Not found"].shape[0]
    print("Notice parsing failed: {}".format(missing_notices))

    missing_results = df[df["Results_long"] == "Not trivial"].shape[0]
    print("No tender results obtained: {}".format(missing_results))