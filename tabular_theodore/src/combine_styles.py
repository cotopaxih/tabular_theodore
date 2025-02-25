import pandas as pd
import os

def df_stats(df1 : pd.DataFrame, df2 : pd.DataFrame = None) -> None:
    """
    Prints information about the datasets to check data quality

    params:
    df1: a dataframe which we want to describe
    df2: optional dataframe which we want to describe and compare with df1
    """
    print("Number of rows in dataframe 1: {}".format(len(df1.shape[0])))
    print("Number of columns in dataframe 1: {}".format(len(df1.columns)))

    if df2 is not None:
        print("Number of rows in dataframe 2: {}".format(len(df2.shape[0])))
        print("Number of columns in dataframe 2: {}".format(len(df2.columns)))
        print("Number of shared columns: {}".format(len(set(df2.columns).intersection(set(df1.columns)))))
    
def import_all_dfs_from_folder(path : str) -> pd.DataFrame:
    """
    If there are multiple dataframes with the same style, we can just concatenate them

    params:
    path: path to the folder we wish to use with forward slash format
    """
    os.chdir(path)  
    files = os.listdir()

    full_df = pd.DataFrame()
    for f in files: 
        if f != "done": # a done folder may be useful if we have already processed some files and we intend to reuse the dataframes
            new_df = pd.read_csv(f, encoding = "utf-8")
            full_df = pd.concat([full_df, new_df])
    
    return full_df

def add_missing_cols(df : pd.DataFrame, cols : list) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = pd.Series()
    return df

def combine_key_cols(df_nr : pd.DataFrame, df_r : pd.DataFrame) -> pd.DataFrame:
    """
    These columns are only a fraction of all, found to be useful for Austria.
    Pay attention to style (arabic vs roman numerals in sections of the tender) because the naming convention is not uniform

    params:
    df_nr: non-roman df
    df_r: roman df 
    """
    df_nr["Filename"] = df_nr.index
    df_r["Filename"] = df_r.index
    file_name = 'Filename'                                       # used to be 'Unnamed: 0'!!!
    date = 'Other_Notice dispatch date'                            # 'Results_Date of dispatch of this notice'

    buyer_name = 'Buyer_Official name'                             # 'Buyer_Official name'
    buyer_email = 'Buyer_Email'                                    # 'Buyer_E-mail'
    buyer_activity = 'Buyer_Activity of the contracting authority' # 'Buyer_Main activity'

    winner_bool = 'Results_Winner selection status'                # 'Results_A contract/lot is awarded'
    winner_name = 'Results_Official name'                          # 'Winner_Official name'

    value_best = 'Results_Value of all contracts awarded in this notice' #'Results_Value of the result', 'Lot_Value'

    cpv = 'Procedure_Main classification ( cpv )'                  # 'Lot_Main CPV code'
    more_cpvs = 'Procedure_Additional classification ( cpv )'      # 'Lot_Additional CPV code(s)', 'Lot_CPV code(s)'

    # 'Procedure_Main nature of the contract', 'Procedure_Main classification ( cpv )', 'Procedure_Additional classification ( cpv )'
    # 'Lot_Main CPV code', 'Lot_Type of contract', 'Lot_Additional CPV code(s)', 'Lot_CPV code(s)'

    title = 'Lot_Title'                                           # 'Lot_Title'
    description = 'Lot_Description'                                # 'Lot_Description'

    df2_cols = ['Buyer_Official name', 'Winner_Official name', 'Lot_Value', 'Lot_Title', 'Lot_Description', 'Lot_Main CPV code', 'Lot_Additional CPV code(s)', 'Buyer_E-mail', 'Buyer_Main activity', 'Results_A contract/lot is awarded', 'Unnamed: 0', 'Results_Date of dispatch of this notice']
    df_r_cols = df2_cols + ['Lot_Short description']
    df_nr_cols = [buyer_name,  winner_name, value_best, title, description, cpv, more_cpvs, buyer_email, buyer_activity, winner_bool, file_name, date]
    

    if df_nr is not None and df_nr.shape[0] > 0:
        df_nr = add_missing_cols(df_nr, df_nr_cols)
        df1_key_parts = df_nr.loc[:, df_nr_cols]
        df1_key_parts.columns = df2_cols
    else:
        df1_key_parts = pd.DataFrame()
    
    if df_r is not None and df_r.shape[0] > 0:
        df_r = add_missing_cols(df_r, df_r_cols) # many missing with test sample bc no results are available
        df2_key_parts = df_r.loc[:, df_r_cols]
    else:
        df2_key_parts = pd.DataFrame()

    combined_df = pd.concat([df1_key_parts, df2_key_parts])
    #combined_df = combined_df.rename(columns = {"Unnamed: 0" : "Filename"})

    return combined_df