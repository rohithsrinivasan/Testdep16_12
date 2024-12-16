import pdfplumber
import pandas as pd
import logging
import tabula

    

    

class TableExtractor:
    def __init__(self, pdfpath):
        """
        Initialize the TableExtractor with the PDF path and keywords to identify pages.
        
        Args:
        - pdfpath (str): Path to the PDF file.
        - start_keywords (list): Keywords to identify the start page.
        - end_keywords (list): Keywords to identify the end page.
        """
        self.pdfpath = pdfpath
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def page_identifier(self, keywords):
        """
        Identify the page number where the keywords are found.
        
        Args:
        - keywords (list): List of keywords to search for.
        
        Returns:
        - int: Page number (1-based index) where keywords are found, or None if not found.
        """
        with pdfplumber.open(self.pdfpath) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()  
                if all(keyword.lower() in text.lower() for keyword in keywords):
                    self.logger.info(f"Keywords {keywords} found on Page {i + 1}")
                    return int(i + 1)
                else:
                    self.logger.debug(f"Keywords {keywords} not found on Page {i + 1}")
        self.logger.error(f"Keywords {keywords} not found in any page.")
        return None
    
    
   

    def extract_tables_singlepage_pdfplumber(self, page_num):
        """
        Extract table data from a specified page.
        
        Args:
        - page_num (int): Page number to extract table from (1-based index).
        - headers (list): List of header names to use for the DataFrame.
        
        Returns:
        - pd.DataFrame: DataFrame containing the table data.
        """
        
        #print(page_num)
        tables_ret = []
        with pdfplumber.open(self.pdfpath) as pdf:
            page = pdf.pages[page_num - 1]  # Convert to 0-based index
            table_settings = {
                "snap_x_tolerance": 4,
                "snap_y_tolerance": 100,
                "horizontal_strategy": "text"
            }
            tables = page.extract_tables()
            
            for table in tables:
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                   
                    tables_ret.append(df)
        
        tables_ret = [df for df in tables_ret if not df.empty and df.dropna(how='all').shape[0] > 0]
              # Return an empty DataFrame if no table is found
        return tables_ret
      
    def extract_tables_singlepage_tabula(self, page_num):
       
        tables = tabula.read_pdf(self.pdfpath, pages=page_num,multiple_tables=True)
        tables = [df for df in tables if not df.empty and df.dropna(how='all').shape[0] > 0]
        return tables

    def identify_table_with_keywords(self, tables, table_specific_keywords):
        matching_tables = []

        # Iterate through each table
        for i, table in enumerate(tables):
            # Convert the column names and table content to strings for easy keyword search
            column_names_str = " ".join(table.columns.astype(str))
            table_values_str = table.astype(str).values.flatten().tolist()
            table_str = column_names_str + " " + " ".join(table_values_str)

            # Check if all keywords are present
            if all(keyword.lower() in table_str.lower() for keyword in table_specific_keywords):
                matching_tables.append(table)

        # Error handling
        if len(matching_tables) == 0:
            print("No table contains all the specified keywords.")
            return pd.DataFrame()
        elif len(matching_tables) > 1:
           print("More than one table contains all the specified keywords.")
           return pd.DataFrame()
        else:
            return matching_tables[0]


   

