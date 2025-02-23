import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from ydata_profiling import ProfileReport
import tempfile

# Set up the app
st.set_page_config(page_title="Data Sweeper App", page_icon="🧊", layout="wide")
st.title("🧊 Data Sweeper App")
st.write("Transform Your Data: Clean, Visualize, and Get Your Perfect CSV in Seconds!")

# File uploader
uploaded_files = st.file_uploader("⬆️ Upload a CSV or Excel file:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file format: {file_ext}")
            continue

        # File info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")

        # Show first 7 rows of data
        st.write("**📈 Data Preview (First 7 Rows):**")
        st.dataframe(df.head(7))

        # Data Summary & Insights
        st.subheader("🗒️ Data Summary")
        if st.checkbox(f"Show Summary for {file.name}"):
            st.write(df.describe())
            st.write("Missing Values Count:")
            st.table(df.isnull().sum())  # Improved table display

        # 2️⃣ Data Cleaning & Transformation
        if st.checkbox(f"🧹 Clean & Transform Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

                if st.button(f"Convert Text Columns to Lowercase for {file.name}"):
                    text_cols = df.select_dtypes(include=["object"]).columns
                    df[text_cols] = df[text_cols].apply(lambda x: x.str.lower())
                    st.success("✅ Text Columns Converted to Lowercase!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if numeric_cols.any():
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing Values Filled!")
                    else:
                        st.warning("⚠️ No numeric columns found for missing value filling.")

                if st.button(f"Remove Special Characters from {file.name}"):
                    text_cols = df.select_dtypes(include=["object"]).columns
                    df[text_cols] = df[text_cols].replace(r'[^A-Za-z0-9 ]+', '', regex=True)
                    st.success("✅ Special Characters Removed!")

        # 3️⃣ Interactive Filtering & Sorting
        st.subheader("📌 Filter Data")
        selected_col = st.selectbox(f"Select Column to Filter {file.name}", df.columns)
        unique_vals = df[selected_col].unique()
        selected_vals = st.multiselect(f"Choose values from {selected_col}", unique_vals, default=unique_vals)
        df = df[df[selected_col].isin(selected_vals)]

       

        # 4️⃣ AI-Powered Data Insights (Pandas Profiling)
        st.subheader("📋 AI-Powered Data Report")
        if st.checkbox(f"Generate AI Report for {file.name}"):
            profile = ProfileReport(df, explorative=True)

            # Save the report to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                profile.to_file(tmp_file.name)
                temp_filename = tmp_file.name

            with open(temp_filename, "r", encoding="utf-8") as file:
                report_html = file.read()

            st.components.v1.html(report_html, height=1000, scrolling=True)

        # Data Visualization
        st.subheader("📊 Data Visualizations")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=["number"])
            if numeric_cols.shape[1] > 1:
                st.bar_chart(numeric_cols.iloc[:, :2])
            else:
                st.warning("⚠️ Not enough numeric columns to generate a bar chart.")

       
        # File Conversion Options
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            st.download_button(
                label=f"⬇️ Download {file_name}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("🎉 All Files Processed!")
