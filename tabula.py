from TableExtractor_class import TableExtractor


pdf_path = "C:/ashish/Automation/Testing/pdf_files/Tested/ISL8117AFRZ.pdf"
pod_table_extractor = TableExtractor(pdf_path)

page_num = pod_table_extractor.page_identifier(
    keywords=[
        "Symbol Parameters"
    ]
)

packageDim_tables_pdfplumber = (
    pod_table_extractor.extract_tables_singlepage_pdfplumber(page_num=page_num)
)
packageDim_tables_pdfplumber[0].to_csv("output.csv")
packageDim_tables_pdfplumber[1].to_csv("output1.csv")
packageDim_tables_pdfplumber[2].to_csv("output2.csv")

print(packageDim_tables_pdfplumber[0])