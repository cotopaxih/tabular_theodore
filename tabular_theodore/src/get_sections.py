#from tabular_theodore import get_buyer, get_procedure, get_lot, get_results, get_other
import pandas as pd
import os
import glob
from ..utils import *

def get_sections_from_notice(filepath :str, dq : bool) -> pd.DataFrame:
    """
    Try to obtain the main sections from the notice, such as Buyer, Procedure or Award of Contract

    param:
    filepath: file of csv dataset where notice has been extracted from raw html page
    dq: Do you wish to see the 
    """
    df = pd.read_csv(filepath).T
    df.columns = list(df.iloc[0, :])

    df["Buyer"] = df["Notice"].apply(lambda x: get_buyer(x)) 
    df["Procedure"] = df["Notice"].apply(lambda x: get_procedure(x))
    df["Results_long"] = df["Notice"].apply(lambda x: get_results(x))
    df["Lot"] = df["Notice"].apply(lambda x: get_lot(x))
    df["Other"] = df["Notice"].apply(lambda x: get_other(x))

    if (dq):
        get_quality_metrics(df)

    return df

def get_sections_from_notices(folder : str, dq_for_each_file : bool) -> pd.DataFrame:
    """
    Try to obtain the main sections from the notice, such as Buyer, Procedure or Award of Contract

    param:
    folder: folder with files of csv datasets where notice has been extracted from raw html page
    """
    working_directory = os.getcwd() 
    os.chdir(folder)
    files = glob.glob('*.csv')

    full_df = pd.DataFrame()

    for f in files:
        df = get_sections_from_notice(f, dq_for_each_file)
        full_df = pd.concat([full_df, df])
    
    full_df = full_df.drop_duplicates().drop("Unnamed: 0")
    os.chdir(working_directory)
    
    print("---------------------------------")
    print("Data quality in combined dataset: ")
    print("---------------------------------")
    get_quality_metrics(full_df)
    print("---------------------------------")

    return full_df