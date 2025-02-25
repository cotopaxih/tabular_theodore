from ..utils.headers_and_fields import *
from ..utils import parse_section, get_romans, get_roman_content, parse_winner, get_winner, four_roman_bins, get_main_part_of_sec5
from datetime import date 
import pandas as pd
import os

def persist_roman_df(full_df: pd.DataFrame, output_dir : str, project: str) -> None:
    """
    Save the dataset as a CSV

    output_dir : the folder where the parsed table should be saved
    """ 
    orig_dir = os.getcwd()
    os.chdir(output_dir)
    if "r" not in os.listdir():
        os.mkdir("r")
    d = date.today().strftime('%d_%m_%Y')
    full_df.to_csv("{dir}/r/TED_romans_df_{date}_{project}.csv".format(dir = output_dir, date = d, project = project), encoding = "utf-8")

    os.chdir(orig_dir)

def parse_romans_wrapper(df : pd.DataFrame, output_dir : str, project : str, save_as_csv : bool = True) -> pd.DataFrame:
    """
    Extract information from intermediate dataframe which already has fields such as Buyer, Lot, Procedure.

    params:
    df : dataframe filtered to contain roman-style headers
    project : relevant for file names, such as 'ROU' or 'AT'
    save_as_csv : should the results be written to a file?
    """

    buyer_parsed = df["Buyer"].apply(lambda x: parse_section(x, buyer_fields, get_romans(x)) if "Official name :" in str(x) else "NOT FOUND")
    lot_parsed = df["Lot"].apply(lambda s: parse_section(s, lot_fields, get_romans(s)))
    procedure_parsed = df["Procedure"].apply(lambda s: parse_section(s, proc_fields_unnumbered, get_romans(s)))

    df_roman_bins = df["Results_long"].apply(lambda x: four_roman_bins(get_romans(x.split("Section VI")[0])))
    df_eur_value = df["Results_long"].apply(lambda x: ("EUR" in x) and (four_roman_bins(get_romans(x.split("Section VI")[0]))== "normal roman"))
    print("Roman structure with EUR value assigned: " + str(df_eur_value.sum()))
    roman_indices = df_roman_bins[df_roman_bins == "normal roman"].index
    sec5_roman_df = df.loc[roman_indices, "Results_long"].apply(lambda x: x.split("Section VI")[0])
    df_pre5 = sec5_roman_df.apply(lambda x: x.split(get_romans(x)[0])[0])
    df_res_intro = df_pre5.apply(lambda x: parse_section(x, pre_section_titles, get_romans(x)))

    sec5_roman_parsed = sec5_roman_df.apply(lambda x: parse_section(get_main_part_of_sec5(x), subheaders, get_romans(x))) # includes winner
    winner = sec5_roman_parsed.apply(lambda x: get_winner(x, buyer_fields))

    ### alternative currently not used - seems to be working equally fine
    winner2 = df["Results_long"].apply(lambda x: parse_winner(x, header_list+subheaders + lot_fields + all_fields) if "Section VI" in x else "NOT ROMAN?")

    sec6_roman_df = df.loc[roman_indices, "Results_long"].apply(lambda x: "Section VI" + "Section VI".join(x.split("Section VI")[1:]))
    sec6_roman_parsed = sec6_roman_df.apply(lambda x: parse_section(x, sec6_headers, get_romans(x))) # review body remains collapsed (irrelevant ig)
    res_parsed = sec6_roman_parsed
    other_parsed = df["Other"].apply(lambda s: parse_section(s, other_fields, []))

    l = [buyer_parsed, procedure_parsed, df_res_intro, res_parsed,winner, lot_parsed, other_parsed]
    prefixes = ["Buyer", "Procedure", "Results", "Results", "Winner", "Lot", "Other"]

    full_df = pd.DataFrame()
    for prefix, data in zip(prefixes, l):
        data = data.apply(pd.Series) # creating a df by transforming dictionaries to Series
        if len(data) > 0:
            data.columns = [prefix + "_" + str(c) for c in data.columns]
            full_df = pd.concat([full_df, data], axis = 1)
    
    if save_as_csv:
        persist_roman_df(full_df, output_dir, project)
    
    return full_df