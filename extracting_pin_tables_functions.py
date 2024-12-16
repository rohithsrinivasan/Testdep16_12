import pdfplumber
import re
import pandas as pd
import tabula
import numpy as np
import json


def find_matching_lines(pdf_path, page_number_list, pin_keyword, package_keyword):
    matching_lines = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_number_list:
            if page_number > len(pdf.pages):
                print(f"Skipping page {page_number} - exceeds total number of pages ({len(pdf.pages)})")
                continue

            text = pdf.pages[page_number - 1].extract_text()

            for line in text.split('\n'):
                if pin_keyword.lower() in line.lower() and package_keyword.lower() in line.lower():
                    matching_lines[line] = page_number  # Use line as key, page_number as value
    return matching_lines

def find_table_starting_and_stopping_based_on_pin_string(pdf_path, page_number_list, pin_keyword, package_keyword, part_number):
    # Get matching lines from the modified function
    matching_lines = find_matching_lines(pdf_path, page_number_list, pin_keyword, package_keyword)

    if len(matching_lines) == 1:
        # Loop through the matching lines dictionary to get the line and its corresponding page number
        for line, page_number in matching_lines.items():
            words = line.split()

            # Regular case: Two words, with the first matching the section format
            if len(words) == 2 and re.match(r'^[A-Z0-9]\.\d+\.\d+$', words[0]):
                section_number = words[0]
                sections = section_number.split('.')
                sections[-1] = str(int(sections[-1]) + 1)  # Increment the last section
                next_section_number = '.'.join(sections)
                print(f"Regular case found: Section {section_number} -> Next Section {next_section_number}")

                # Open the PDF file using pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    new_next_section_number, ending_page_number = find_ending_page(
                        pdf, page_number_list, next_section_number
                    )

                return page_number, section_number, new_next_section_number, ending_page_number

            # Special case: Line has parentheses
            elif len(words) > 2 and re.match(r'^[A-Z0-9]\.\d+\.\d+$', words[0]) and '(' in line:
                section_number = words[0]
                sections = section_number.split('.')
                sections[-1] = str(int(sections[-1]) + 1)  # Increment the last section
                next_section_number = '.'.join(sections)

                # Extract text inside parentheses
                match = re.search(r'\((.*?)\)', line)
                if match:
                    text_in_parentheses = match.group(1)
                    print(f"Special case detected on page {page_number}:")
                    print(f"  Section {section_number} -> Next Section {next_section_number}")
                    print(f"  Text inside parentheses: {text_in_parentheses}")

                # Open the PDF file using pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    new_next_section_number, ending_page_number = find_ending_page(
                        pdf, page_number_list, next_section_number
                    )

                return page_number, section_number, new_next_section_number, ending_page_number

    else:
        print("You have more than one Pin table with the same pin package details.")
        #print(matching_lines)
        
        # Step 1: Extract 4 lines of text below each of those lines in matching_lines
        lines_below = {}  # Store lines below each matching line
        with pdfplumber.open(pdf_path) as pdf:
            for line, page_number in matching_lines.items():
                page = pdf.pages[page_number - 1]  # Get the page based on the page_number
                text = page.extract_text()
                lines = text.split('\n')

                # Find the index of the matching line
                try:
                    matching_index = lines.index(line)
                    lines_below[line] = lines[matching_index + 1: matching_index + 5]  # Extract 4 lines below
                except ValueError:
                    print(f"Error: Line '{line}' not found on page {page_number}")


        # Step 2: Find which of those 4 lines contains the 'f{part_number}' string
        matched_line = None
        new_matched_line = None
        for line, lines in lines_below.items():
            for extracted_line in lines:
                if f"{part_number}" in extracted_line:
                    matched_line = extracted_line
                    print(f"Found part number in line: {matched_line}")
                    print(f"Found in line from lines_below: {line}")
                    new_matched_line = line
                    # Print the table starting page number
                    starting_page_number = matching_lines[line]
                    print(f"Table starting page number: {starting_page_number}")
                    break
            if new_matched_line:
                break


        # Step 3: Process the matched line
        if new_matched_line:
            words = new_matched_line.split()
            #print(f"Words :{words}")

            # Regular case: Two words, with the first matching the section format
            if len(words) == 2 and re.match(r'^[A-Z0-9]\.\d+\.\d+$', words[0]):
                section_number = words[0]
                sections = section_number.split('.')
                sections[-1] = str(int(sections[-1]) + 1)  # Increment the last section
                next_section_number = '.'.join(sections)
                print(f"Regular case found: Section {section_number} -> Next Section {next_section_number}")

                # Open the PDF file using pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    new_next_section_number, ending_page_number = find_ending_page(
                        pdf, page_number_list, next_section_number
                    )

                return starting_page_number, section_number, new_next_section_number, ending_page_number

            # Special case: Line has parentheses
            elif len(words) > 2 and re.match(r'^[A-Z0-9]\.\d+\.\d+$', words[0]) and '(' in new_matched_line :
                section_number = words[0]
                sections = section_number.split('.')
                sections[-1] = str(int(sections[-1]) + 1)  # Increment the last section
                next_section_number = '.'.join(sections)

                match = re.search(r'\((.*?)\)', new_matched_line)  # non-greedy match inside parentheses
                if not match:
                    # If no closing parenthesis was found, match up to the first non-closing parenthesis
                    match = re.search(r'\((.*)', new_matched_line)


                if match:
                    text_in_parentheses = match.group(1)
                    print(f"Special case detected on page {page_number}:")
                    print(f"  Section {section_number} -> Next Section {next_section_number}")
                    print(f"  Text inside parentheses: {text_in_parentheses}")

                # Open the PDF file using pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    new_next_section_number, ending_page_number = find_ending_page(
                        pdf, page_number_list, next_section_number
                    )

                return starting_page_number, section_number, new_next_section_number, ending_page_number
            
            else:
                print(f"Something is wrong this case want expected, it didnt enter both loops")


        else:
            print("Part number not found in the extracted lines.")

    return None

                   

def find_ending_page(pdf, page_number_list, next_section_number):
    next_section_number = next_section_number.lower()

    for page_num in page_number_list:
        if page_num <= 0:
            continue
        text = pdf.pages[page_num - 1].extract_text().lower()
        if next_section_number in text:
            return next_section_number.upper(), page_num

    print(f"'{next_section_number}' not found in specified pages. Using 'Symbol Parameters' as ending point.")
    return "Symbol Parameters", page_number_list[-1]

def find_ending_page(pdf, page_number_list, next_section_number):

    # Iterate through the specified page numbers to find the next section number
    for page_num in page_number_list:
        page_text = pdf.pages[page_num - 1].extract_text()
        if next_section_number in page_text:
            # If found, return the next section number and page number
            new_next_section_number = next_section_number
            return new_next_section_number, page_num

    # If not found, use "Symbol Parameters" as the ending point
    print(f"'{next_section_number}' not found in specified pages. Using 'Symbol Parameters' as ending point.")
    new_next_section_number = "Symbol Parameters"
    page_num = page_number_list[-1]

    return new_next_section_number, page_num



def generate_list_of_page_numbers(start, end):
  if start > end:
    return None  # Invalid input: start > end

  return list(range(start, end + 1))

def extracting_pin_tables_in_pages(file_path, my_list_of_pages):
    dfs = tabula.read_pdf(file_path, pages= my_list_of_pages, multiple_tables=True, lattice= True)
    #print(f"Raw dataframe :{dfs}" )
    dfs = [df for df in dfs if not df.empty and df.dropna(how='all').shape[0] > 0]
    modified_dfs = []
    for df in dfs:
        modified_df = df.replace(to_replace=r'^Unnamed:.*', value=np.nan, regex=True)
        modified_df = modified_df.apply(lambda x: pd.Series(x.dropna().values), axis=1)
        modified_df = modified_df.applymap(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)
        modified_df = modified_df.drop(modified_df[modified_df.isin(['Designator']).any(axis=1)].index)

        if modified_df.shape[1] == 4:
            #print("DataFrame has 4 columns as expected")
            # Assign expected column names ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name']
            modified_df.columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name']
            modified_dfs.append(modified_df)
        else:
            print(f"Unexpected number of columns: {modified_df.shape[1]}")

    #if len(modified_dfs) == 1:
        #return modified_dfs[0]
    return modified_dfs

def extract_table_as_text(pdf_path, page_number_list, start_string, ending_string):
    with pdfplumber.open(pdf_path) as pdf:
        texts = []
        capturing = False
        extracted_text = ""
        
        for page_number in page_number_list:
            if page_number > len(pdf.pages):
                continue
            page = pdf.pages[page_number - 1]
            text = page.extract_text()
            
            if text:
                if capturing:
                    end_index = text.find(ending_string)
                    if end_index != -1:
                        extracted_text += text[:end_index + len(ending_string)]
                        texts.append(extracted_text)
                        capturing = False
                        extracted_text = ""
                    else:
                        extracted_text += text
                if start_string in text and not capturing:
                    start_index = text.find(start_string)
                    extracted_text = text[start_index:]
                    capturing = True
                    end_index = text.find(ending_string, start_index)
                    if end_index != -1:
                        extracted_text = text[start_index:end_index + len(ending_string)]
                        texts.append(extracted_text)
                        capturing = False
                        extracted_text = ""
        
        if capturing:
            texts.append(extracted_text)
        
        return "\n".join(texts) if texts else None

def text_filter(input_string):
    lines = input_string.splitlines()
    filtered_lines = [
        line for line in lines 
        if not (
            line.startswith('Pin') or
            line.startswith('Designator') or
            line.startswith('Name') or
            line.count(',') > 4 or  # Condition 1: More than 4 commas
            'Applicable Part Numbers' in line  # Condition 2: Contains "Applicable Part Numbers"
        )
    ]

    return '\n'.join(filtered_lines)



def df_to_string(df):
  string_representation = ""
  for index, row in df.iterrows():
    row_string = " ".join(str(value) for value in row)
    string_representation += row_string + "\n"
  return string_representation    


def combine_dataframes_and_print_dictionary(dfs):

    #if len(dfs) == 1:
        #return dfs[0]
    
    # Create a dictionary of DataFrame indices and their string representations
    df_strings = {i + 1: df_to_string(df) for i, df in enumerate(dfs)}

    # Generate all possible combinations of DataFrame indices and combine their text
    combo_dict = {}
    for i in range(len(df_strings)):
        for j in range(i + 1, len(df_strings) + 1):
            combo_keys = tuple(range(i + 1, j + 1))
            combo_values = "\n".join([df_strings[k] for k in combo_keys])
            combo_dict[combo_keys] = combo_values

    num = len (combo_dict)    
    return combo_dict, num

def filter_top_3_by_size(combo_dict, input_string):
    size_diffs = {combo_keys: abs(len(combo_value) - len(input_string)) 
                  for combo_keys, combo_value in combo_dict.items()}
    sorted_size_diffs = dict(sorted(size_diffs.items(), key=lambda x: x[1]))
    top_3 = {k: sorted_size_diffs[k] for k in list(sorted_size_diffs)[:3]}  
    return top_3

def filter_combo_dict_based_on_size_filter(dict1, dict2):
    # Retain only the key-value pairs in dict1 if the key is also present in dict2
    filtered_dict = {key: dict1[key] for key in dict2 if key in dict1}
    return filtered_dict


def calculate_differences(input_dict, input_string):
  input_lines = set(input_string.splitlines())
  result = {}

  for key, value_string in input_dict.items():
    value_lines = set(value_string.splitlines())
    extra_lines = max(abs(len(value_lines - input_lines)), abs(len(input_lines - value_lines)))
    result[key] = extra_lines

  return result

def find_best_match(differences):
    min_value = min(differences.values())
    min_keys = [key for key, value in differences.items() if value == min_value]

    if len(min_keys) > 1:
        # If multiple keys have the same minimum difference, choose the shortest key
        lengths = [len(str(k)) for k in min_keys] #Calculate lengths of all min keys
        if len(set(lengths))==1: #Check if all lengths are same
            print("Rare Exception Case: Multiple keys have the same minimum difference and same length.")
        min_key = min(min_keys, key=lambda k: len(str(k)))
    else:
        min_key = min_keys[0]

    return min_key

def get_dataframes_from_tuple(dataframes_list, index_tuple):

    if any(i > len(dataframes_list) or i < 1 for i in index_tuple):
        raise IndexError("Index out of range of DataFrame list.")

    selected_dataframes = [dataframes_list[i-1] for i in index_tuple]
    number = len(selected_dataframes)
    
    return selected_dataframes, number



def find_matching_dfs(dfs, table_as_text):
   
    #setting this for easy comparison
    target_words = set(table_as_text.split())
    # Create a dictionary of table numbers (index) and DataFrame strings
    df_strings = {i + 1: df_to_string(df) for i, df in enumerate(dfs)}
    
    # Generate all possible combinations of DataFrame strings and combine them
    combo_dict = {}
    for i in range(len(df_strings)):
        for j in range(i + 1, len(df_strings) + 1):
            combo_keys = tuple(range(i + 1, j + 1))
            combo_values = "\n".join([df_strings[k] for k in combo_keys])
            combo_dict[combo_keys] = combo_values


    # Find the best match
    # Initialize variables to track the best match
    best_match_keys = None
    max_word_matches = 0
    min_extra_noise = float('inf')
    
    # Iterate through the combinations and find the best match
    for keys, combined_text in combo_dict.items():
        combined_words = set(combined_text.split())
        
        # Find words that match the target
        matching_words = combined_words & target_words
        word_match_count = len(matching_words)
        
        # Extra noise is the number of words in combined_text that don't match table_as_text
        extra_noise = len(combined_words - target_words)
        
        # Update best match based on match count and noise
        if word_match_count > max_word_matches or (word_match_count == max_word_matches and extra_noise < min_extra_noise):
            best_match_keys = keys
            max_word_matches = word_match_count
            min_extra_noise = extra_noise

    return best_match_keys
