import os
import streamlit as st
import pandas as pd
from tabula import read_pdf
import SideAllocation_functions
from dotenv import load_dotenv
import google.generativeai as genai
import functions as f
import datetime

st.set_page_config(page_icon= 'dados/logo_small.png', page_title= "SymbolGen" )

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
#st.markdown(hide_st_style, unsafe_allow_html=True)


f.header_intro()
f.header_intro_2()

st.subheader("Side Allocation Page")


if "part_number" not in st.session_state and "input_csv_name" not in st.session_state:
    st.error("Please fill in Interface/grouping pages first. Data is missing to proceed.")

try:
    part_number = st.session_state['part_number']
    input_csv_file_name = st.session_state['input_csv_name']
except KeyError:
    part_number = "Part_Number_Not defined"
    input_csv_file_name = "input_csv_file_name_not_defined"

if 'grouped_pin_table' in st.session_state:
    grouped_pin_table = st.session_state['grouped_pin_table']

    #st.write("Grouped Pin Table:")
    #st.dataframe(grouped_pin_table)

    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority']
    additional_column = 'Priority'
    before_priority_flag, added_empty_priority_column = SideAllocation_functions.check_excel_format(grouped_pin_table,required_columns, additional_column)
    #st.text(f"Before Side Allocation Flag :{before_priority_flag}")
    #st.dataframe(added_empty_priority_column)
    priority_added = SideAllocation_functions.assigning_priority_for_group(added_empty_priority_column)
    #st.text(f"Priority Column Added")
    #st.dataframe(priority_added)

    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority', 'Side']
    additional_column = 'Side'
    before_side_flag, added_empty_side_column = SideAllocation_functions.check_excel_format(priority_added,required_columns, additional_column)
    #st.text(f"Before Side Allocation Flag :{before_side_flag}")
    #st.dataframe(added_empty_side_column)

    if len(added_empty_side_column) < 80:
        side_added = SideAllocation_functions.assigning_side_for_priority(added_empty_side_column)
        #st.text(f"Side Column Added")
        #st.dataframe(side_added)

    else:
        st.text(f"Executing Partioning")
        df_dict = SideAllocation_functions.partitioning(added_empty_side_column)
        #st.text("Raw data dict")
        #for subheader, dataframe in df_dict.items():
        #    st.subheader(subheader)
        #    st.dataframe(dataframe)
        side_added_dict = SideAllocation_functions.assigning_side_for_priority_for_dataframes_within_dictionary(df_dict)
        st.text(f"Side Column Added")
        #for subheader, dataframe in side_added_dict.items():
        #    st.subheader(subheader)
        #    st.dataframe(dataframe)


        #side_added = SideAllocation_functions.convert_dict_to_list(df_dict)
        side_added = side_added_dict

    st.text("Choose Layout Style")
    changing_as_per_style_guide = st.checkbox("Layout Style : DIL")

    if changing_as_per_style_guide:

        required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority', 'Side', 'Changed Grouping']
        additional_column = 'Changed Grouping'
        before_new_grouping_flag, added_empty_new_grouping_column = SideAllocation_functions.check_excel_format(side_added,required_columns, additional_column)        


        grouping_changed = SideAllocation_functions.Dual_in_line_as_per_Renesas(added_empty_new_grouping_column)
        #st.text(f"DIL template as per Renesas")

        if isinstance(grouping_changed, pd.DataFrame):
            grouping_changed = SideAllocation_functions.final_filter(grouping_changed) 
            st.subheader(f"Smart_Table: ")
            st.dataframe(grouping_changed)  # Display single DataFrame
            #st.success("Side Alloction Done!")

            timestamp = datetime.datetime.now().strftime("%d-%m_%H:%M")
            try:
                filename = f"{part_number}_SmartPinTable_{timestamp}.csv"
            except NameError:
                try:
                    filename = f"{input_csv_file_name}_SmartPinTable_{timestamp}.csv"
                except NameError:
                    print("Error: File name could not be generated. Please check the variables 'part_number' and 'input_csv_file_name'.")
                    filename = "None"           

            if st.download_button(
                label="Download Smart Table",
                data=grouping_changed.to_csv(index=False),
                file_name=filename,
                mime='text/csv',
                type="primary"
            ):
                st.session_state['downloaded'] = True  # Record download status
                st.success("Download completed. You can now proceed.")  

            else:
                 st.write("Download to proceed.")                  



        # Assuming `grouping_changed` is a dictionary of DataFrames
        elif isinstance(grouping_changed, dict):
            for key, df in grouping_changed.items():
                if not df.empty:
                    df = SideAllocation_functions.final_filter(df)   
                    st.subheader(f"Smart_Table: {key}")  # Display the key as a subheader
                    st.dataframe(df)

            # Prepare the filename
            timestamp = datetime.datetime.now().strftime("%d-%m_%H:%M")
            filename = f"{part_number}_SmartPinTable_{timestamp}.xlsx"

            # Save to an Excel file with multiple sheets using 'openpyxl'
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in grouping_changed.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Read the Excel file as binary to enable download
            with open(filename, 'rb') as f:
                excel_data = f.read()

            # Provide download button for the Excel file
            if st.download_button(
                label="Download All",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            ):
                st.session_state['downloaded'] = True  # Record download status
                st.success("Download completed. You can now proceed.")  
                
            else:
                 st.write("Download to proceed")  

        else:   
            st.text(f"Error Occured in Displaying Dataframes")

        st.success("Done!")

else:
    st.write("No Grouped Pin table available.") 


if 'downloaded' in st.session_state and st.session_state['downloaded'] == True:
    st.page_link("pages/symbol-parameters.py",label="Next : symbol-parameters")
else:
    print("No File download available, User has to download the csv")    

