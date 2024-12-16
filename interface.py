from os import read
import streamlit as st
import pandas as pd
from tabula import read_pdf
import functions as f
import time

st.set_page_config(page_icon= 'dados/logo_small.png', page_title= "SymbolGen" )

#st.page_link("interface.py", label="Extraction")
#st.page_link("pages/grouping.py", label="Grouping")
#st.page_link("pages/side_allocation.py", label="SideAlloc")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
#st.markdown(hide_st_style, unsafe_allow_html=True)

f.renesas_logo()
f.header_intro() 
f.header_intro_2()

#st.subheader('Upload your PDF by clicking on "Browse Files"')
input_buffer = st.file_uploader("Upload a file", type=("PDF"))
input_part_number = st.text_input("Enter a valid Part Number")
input_loaded = False

# Store in session state
if "input_loaded" not in st.session_state:
    st.session_state.input_loaded = False

if input_buffer:
    st.session_state.input_buffer = input_buffer

#st.subheader("Extraction Page") 
if input_buffer:
    if input_part_number:
        with st.spinner('Processing...'):
            time.sleep(5)
            part_number, number_of_pins, package_type, package_code = f.part_number_details(input_part_number, input_buffer)

            if part_number:
                st.session_state.part_number = part_number
            st.session_state['part_number'] = part_number

            # Initialize a session state variable to track used keys
            if "used_keys" not in st.session_state:
                st.session_state["used_keys"] = []

            #pin_table = f.extracting_pin_tables(input_buffer, part_number, number_of_pins, package_type, package_code)
            noise_calculation_combo_dict,dfs = f.extracting_pin_tables_2(input_buffer, part_number, number_of_pins, package_type, package_code)
            st.text(f"Mapping After noise filter Algo : {noise_calculation_combo_dict}")
            pin_table = f.finding_closest_match_for_user(noise_calculation_combo_dict,dfs)
            if pin_table is not None:
                st.subheader("Extracted Pin Table")
                st.dataframe(pin_table) 
            # Handle "Generate Next Match" button
            f.handle_generate_next_match_button(noise_calculation_combo_dict, dfs)       

        st.success("Done!")
        st.session_state['pin_table'] = pin_table
        if "page" in st.session_state and st.session_state["page"] == "grouping":
            st.page_link("pages/grouping.py",label="Next : Grouping")            
        else:
            st.write("Pin table displayed")        

    else:
        st.warning("Please enter a valid Part Number.")
else:
    st.info("Please upload a PDF file.")   
