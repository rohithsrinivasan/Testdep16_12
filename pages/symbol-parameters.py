import streamlit as st
from tabula import read_pdf
from dotenv import load_dotenv
import functions as f
import datetime
import pandas as pd


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

st.subheader("Parameter Extraction Page")

# Check if session state contains required data
if "input_buffer" in st.session_state and "part_number" in st.session_state:
    input_buffer = st.session_state.input_buffer
    part_number = st.session_state.part_number

    st.write("File uploaded:", input_buffer.name)
    st.write("Part number entered:", part_number)

    #f.parameter_table_extraction_2(input_buffer)
    parameter_table = f.parameter_table_extraction_2(input_buffer)
    #st.text(parameter_page)
    st.subheader("Extracted_parameter data")
    st.dataframe(parameter_table)

    st.success("Symbol Data Generation is Complete!!") 

else:
    st.warning("No data found in session state. Please upload a file and enter a part number on the main page.")
