import pandas as pd 

def get_block(input, block_start_nr, next_block_nr, block_start_r, next_block_r):
    """ 
    This is a generic function to get big chunks of the notice on the TED website.
    There are two major groups, those with roman numerals (r) as headers, and those with arabic numerals (nr).
    """
    try:
        try:
            if (next_block_nr is not None):
                return input.split(block_start_nr)[1].split(next_block_nr)[0]
            else:
                return input.split(block_start_nr)[1]
        except:
            if (next_block_r is not None):
                return input.split(block_start_r)[1].split(next_block_r)[0]
            else:
                return input.split(block_start_r)[1]
    except:
        return "Not trivial"

def get_buyer(input):
    return get_block(input, "1.  Buyer", "2.  Procedure", "Section I :  Contracting ", "Section II") # can be authority or entity
def get_procedure(input):
    return get_block(input, "2.  Procedure", "5.  Lot", "Section IV :  Procedure", "Section V")
def get_lot(input):
    return get_block(input, "5.  Lot", "6.  Results", "Section II :  Object", "Section IV")
def get_results(input):
    return get_block(input, "6.  Results", None, "Section V :  Award of contract", None)
def get_other(input):
    return get_block(input, "11.  Notice", None, "Section VI :  Complementary information", None)

def get_main_blocks(df : pd.DataFrame) -> pd.DataFrame:
    """
    Extract main blocks from Notice 

    params:
    df : dataframe derived from html pages
    """
    df["Buyer"] = df["Notice"].apply(lambda x: get_buyer(x)) 
    df["Procedure"] = df["Notice"].apply(lambda x: get_procedure(x))
    df["Results_long"] = df["Notice"].apply(lambda x: get_results(x))
    df["Lot"] = df["Notice"].apply(lambda x: get_lot(x))
    df["Other"] = df["Notice"].apply(lambda x: get_other(x))

    return df