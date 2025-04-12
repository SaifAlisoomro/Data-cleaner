import streamlit as st
import pandas as pd
from io import BytesIO

# Set page config
st.set_page_config(page_title="📁 File Converter & Cleaner", layout="wide")
st.title("📁 File Converter & Cleaner")
st.write("Upload your CSV or Excel files to clean the data and convert them to other formats.")

# File uploader
file_upload = st.file_uploader(
    "Upload a CSV or Excel file", 
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if file_upload:
    for file_index, file in enumerate(file_upload):
        ext = file.name.split(".")[-1]
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

        st.subheader(f"🔍 Preview: {file.name}")
        st.dataframe(df.head())

        # Fill missing values
        if st.checkbox(f"Fill missing values in {file.name}", key=f"fill_{file_index}"):
            df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            st.success("✅ Missing values filled with column mean.")
            st.dataframe(df.head())

        # Drop selected columns
        select_col = st.multiselect(
            f"Select columns to drop from {file.name}", 
            df.columns, 
            default=[],
            key=f"drop_cols_{file_index}"
        )

        if select_col:
            df = df.drop(columns=select_col)
            st.success(f"✅ Dropped columns: {', '.join(select_col)}")
            st.dataframe(df.head())

        # Show chart if numeric columns exist
        numeric_df = df.select_dtypes(include=["number"])
        if not numeric_df.empty:
            if st.checkbox(f"📊 Show chart for {file.name}", key=f"chart_{file_index}"):
                st.bar_chart(numeric_df.iloc[:, 0:2])

        # File conversion options
        format_options = st.radio(
            f"Convert to format for {file.name}:", 
            ["CSV", "Excel"], 
            key=f"format_{file_index}"
        )

        if st.button(f"Generate Download for {file.name}", key=f"generate_{file_index}"):
            if format_options == "CSV":
                output = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=output,
                    file_name=f"{file.name.split('.')[0]}_cleaned.csv",
                    mime="text/csv",
                    key=f"dl_csv_{file_index}"
                )
            else:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                    writer.save()
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"{file.name.split('.')[0]}_cleaned.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_excel_{file_index}"
                )
