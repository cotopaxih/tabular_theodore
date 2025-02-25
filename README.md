This package was made to allow working with the TED EU database efficiently. It scrapes pages and parses their contents to find relevant documents and data.  First try to export what you need directly using their tool (limited to ~150k fields)

The output is a dataframe with the most important pieces of information (~10% of all fields).  

The initial use case was with Zeiss RMS, finding the market size for electron microscopes. Working with the data, competitor analysis emerged as an additional use case. 

### Scrape pages based on manually exported Excel file 
from tabular_theodore import *  

excel_path = "C:/Users/YOURUSER/Downloads/ROU_TED_14-01-2025.xlsx"  
base = "C:/path/to/folder/to/store/files/"  
project = "Test Full Pipeline 10 pages"  

segmented_df, remaining_links_to_scrape = full_pipeline(excel_path=excel_path,  
              base=base,   
              project=project,  
              chunksize=10)  

### Parse already scraped html files 
from tabular_theodore import *  
import os  

base = "C:/path/to/folder/to/store/files/"  
project = "Name as you like"

all_dates = os.listdir(base + project + "/unparsed raw pages")  
segmented_df = parse_pipeline(base = base,   
                              project = project,   
                              scrape_dir = base + project + "/unparsed raw pages",   
                              scrape_dates = all_dates)  

### Scrape only pages which pass a filter (add alternative keywords to data/keywords.json for other projects)

import sys  
import os   

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))   
from tabular_theodore import get_urls, filtered_scrape  

excel_path = "C:/Users/YOURUSER/Downloads/ROU_TED_14-01-2025.xlsx"  
full_url_list = get_urls(excel_path)  
base = "C:/path/to/folder/to/store/files/"    
project = "Test Project (pre-filtered)"  
scrape_dir = base + project + "/unparsed raw pages"  
  
unchecked_urls = filtered_scrape(full_url_list, scrape_dir, True, ["microscopy"], 2) # only visits two pages (last argument), remaining links are returned  
