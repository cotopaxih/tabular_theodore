import re 

def subheader_ordered(input: list) -> list: # only removes the first incorrect member (very few unordered anyway)
    max = 0
    ind = 0
    for i in input:
        subheader_number = i.split(".")[1].split(".")[0]
        if (int(max) > int(subheader_number)):
            print("Correcting odd sequence of subheader numbers by removing entry at index {index} from: {orig_list}".format(index = ind, orig_list = str(input)))
            print(input.pop(ind - 1))
            return input
        else:
            max = int(subheader_number)
            ind += 1
    return input

def get_proc_sections(input : list) -> list: 
    res = re.findall("2\.[0-9]\.[0-9]?[0-9]?\.?", input)
    return subheader_ordered(res)

def get_lot_sections(input : list) -> list: 
    res = re.findall("5\.[0-9]\.[0-9]?[0-9]?\.?", input)
    return subheader_ordered(res)

def get_res_sections(input : list) -> list: 
    res = re.findall("6\.[0-9]\.[0-9]?[0-9]?\.?", input)
    return subheader_ordered(res)

def get_romans(input): 
    patterns = ["IX\.[0-9]\.[0-9]?[0-9]?\.?","X\.[0-9]\.[0-9]?[0-9]?\.?","VIII\.[0-9]\.[0-9]?[0-9]?\.?","VII\.[0-9]\.[0-9]?[0-9]?\.?","VI\.[0-9]\.[0-9]?[0-9]?\.?","IV\.[0-9]\.[0-9]?[0-9]?\.?","V\.[0-9]\.[0-9]?[0-9]?\.?", "III\.[0-9]\.[0-9]?[0-9]?\.?", "II\.[0-9]\.[0-9]?[0-9]?\.?", "I\.[0-9]\.[0-9]?[0-9]?\.?"]
    
    for i in patterns:
        res = re.findall(i, input)
        if len(res) > 0:
            return res
    return []

def get_roman_content(input, romans):
    res = []
    for i in romans[1:]:
        new_res = input.split(i)[0]
        res.append(new_res)
        if i != romans[-1]:
            try:
                input = i.join(input.split(i)[1:])
            except:
                print("Something did not work as expected. Input was:")
                print(input)
        else:
            
            new_res = input.split(i)[1]
            res.append(new_res)
    return res

def parse_buyer(input : str, header_list : list) -> dict:
    found_sections = []
    for h in header_list:
        if h in input:
            found_sections.append(h)
    res = dict()
    for i in range(len(found_sections)):
        if i != len(found_sections) -1:
            next_section = found_sections[i + 1]
            field_content = input.split(found_sections[i])[1].split(next_section)[0].strip()
            if field_content.startswith(":"):
                field_content = field_content[1:].strip()
        else:
            field_content = input.split(found_sections[i])[1].strip()
            if field_content.startswith(":"):
                field_content = field_content[1:].strip()
        if not (found_sections[i] == "Internet address" and field_content.startswith("(es)")): # last one is just a duplicate for the addresses which we do not need
            if not (found_sections[i] == "Description" and field_content.startswith("of the procurement")): 
                res[found_sections[i]]  = field_content
    return res

def parse_section(input : str, header_list : list, romans : list) -> dict:
    found_sections = []
    for h in header_list:
        if h in input:
            found_sections.append(h)
    
    found_index = []
    for i in found_sections:
        found_index.append(input.index(i))
    ordered_found_sections = [x for _, x in sorted(zip(found_index, found_sections))]
    found_sections = list(dict.fromkeys(ordered_found_sections)) # unclear whether this is better (purpose = ordered set to avoid repetition)

    romans # no longer calculated on the spot romans

    res = dict()
    for i in range(len(found_sections)):
        if i != len(found_sections) -1:
            next_section = found_sections[i + 1]
            field_content = input.split(found_sections[i])[1].split(next_section)[0].strip()
            if field_content.startswith(":"):
                field_content = field_content[1:].strip()
        else:
            field_content = input.split(found_sections[i])[1].strip()
            if field_content.startswith(":"):
                field_content = field_content[1:].strip()
        if (found_sections[i] == "The procurement is covered by the Government Procurement Agreement (GPA)" and "Additional inf" in field_content):
            res[re.sub(r'\s+', ' ', found_sections[i])] = field_content.split("Additional inf")[0].strip()
            field_content2 = "Additional inf" + field_content.split("Additional inf")[1].strip()
            for roman in romans:
                if field_content2.strip().endswith(roman):
                    field_content2 = field_content2.removesuffix(roman)
            res["GPA Additional info"] = field_content2.strip()
        else:
            if not (found_sections[i] == "Internet address" and field_content.startswith("(es)")): # last one is just a duplicate for the addresses which we do not need
                if not (found_sections[i] == "Description" and field_content.startswith("of the procurement")): 
                    for roman in romans:
                        if field_content.strip().endswith(roman):
                            field_content = field_content.removesuffix(roman)
                    res[re.sub(r'\s+', ' ', found_sections[i])]  = re.sub(r'\s+', ' ', field_content.replace("\xa0", " ").strip()) 
    return res

def Merge(dict1: dict, dict2: dict) -> dict:
    for i in dict2.keys():
        if i not in dict1:
            dict1[i]=dict2[i]
        else:
            dict1[i + "(1)"]=dict2[i]
    return dict1

def parse_nonroman_winner(input: str, fields: list) -> dict:
    if "8.  Organisations" in input:
        input = input.split("8.  Organisations")[0]
    res_sections = get_res_sections(input)

    chunks = []
    for i in res_sections:
        next_chunk = input.split(i)[0]
        input = str(i).join(input.split(i)[1:])
        chunks.append(next_chunk)
    chunks.append(input)

    res = dict()
    for c in chunks:
        chunk_res = parse_section(c, fields, get_res_sections(c))
        res = Merge(res, chunk_res)
    return res

def parse_winner(sec5, header_list):
    for i in get_roman_content(sec5, get_romans(sec5)):
        if "Name and address of the contractor" in i:
            winner = parse_buyer(i, header_list)
            return winner
        
def test_res_parsing(df, header_list): # used to be in the roman notebook
    sec6_type = df.loc[:, "Results_long"].apply(lambda x: "Section VI" in x)


    winners = []
    failcounter = 0
    fails = []
    for i in sec6_type[sec6_type == True].index:
        s = df.loc[i, "Results_long"]
        sec5 = s.split("Section VI")[0]
        try:
            winner = parse_winner(sec5, header_list)
            if type(winner) != dict:
                if ("is not awarded" in sec5):
                    winner = "No winner - contract not awarded"
                else:
                    winner = parse_buyer(sec5, header_list+subheaders + lot_fields + all_fields) 
            winners.append(winner)
        except:
            failcounter+=1
            fails.append(i) # TODO: handle repeating numbering (multiple winners?) - seems to be solved with parse_buyer and subheaders above

    print("Number of indexing problems in romans: " + str(failcounter)) # same as before 19 fail in get_roman parts
    nones = 0
    for i in winners:
        if type(i) != dict and i != "No winner - contract not awarded":
            nones += 1
    print("Number of unsolved ones: " + str(nones))

def get_winner(x, buyer_fields):
    if "Name and address of the contractor" in x:
        return parse_section(x["Name and address of the contractor"], buyer_fields, get_romans(x["Name and address of the contractor"]))
    else:
        return "NOT FOUND (checked for Microscopy only)"
    
def four_roman_bins(romans):
    if romans == ['V.2.', 'V.2.1.', 'V.2.2.', 'V.2.3.', 'V.2.4.', 'V.2.5.']:
        return "normal roman"
    if romans == ['V.1.', 'V.2.', 'V.3.', 'V.4.', 'V.5.']:
        return "normal roman"
    if romans == []:
        return "non-roman"
    if romans == ['V.1.']:
        return "unsuccessful tender"
    if len(romans) > 1:                   # TODO multiple winners will be in this bin
        return "normal roman"

def get_main_part_of_sec5(x):
    return get_romans(x)[0] + get_romans(x)[0].join(x.split(get_romans(x)[0])[1:])