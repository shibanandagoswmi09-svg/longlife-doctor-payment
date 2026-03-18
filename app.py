import streamlit as st
import pandas as pd

st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")

st.title("🏥 Longlife Clinic - Doctor Payment Module")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Load data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Standardize column names (space remove)
        df.columns = df.columns.str.strip()

        # EXACT LOGIC CALCULATION
        def get_exact_doc_share(row):
            # Excel columns: Fee, Discount
            fee = float(row.get('Fee', 0))
            discount = float(row.get('Discount', 0))
            
            # Net for calculation (Sudhu Fee theke Discount bad, Reg Fee asbe na)
            calc_base = fee - discount
            
            name = str(row.get('Doctor Name', '')).upper()
            
            # Dr. Soumya Chatterjee: 85%
            if "SOUMYA CHATTERJEE" in name:
                return calc_base * 0.85
            # Baki shobai (March ENT + Others): 80%
            else:
                return calc_base * 0.80

        # Apply logic
        df['Doc_Share_Calculated'] = df.apply(get_exact_doc_share, axis=1)
        
        # Clinic Share = (Fee - Discount - Doc Share) + Reg Fee
        df['Clinic_Share_Calculated'] = (df['Fee'] - df['Discount'] - df['Doc_Share_Calculated']) + df['Reg Fee']

        # Grouping for Report
        march_ent_list = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
        df['Group_Name'] = df['Doctor Name'].apply(
            lambda x: "MARCH ENT" if str(x).upper() in march_ent_list else x
        )

        # Display Total
        total_payment = df['Doc_Share_Calculated'].sum()
        
        st.success(f"Calculation Complete!")
        st.metric("Total Doctor's Share", f"₹{total_payment:,.0f}") # ROUNDED TO NEAREST INTEGER

        # Summary Table
        summary = df.groupby('Group_Name').agg({
            'Doc_Share_Calculated': 'sum',
            'Clinic_Share_Calculated': 'sum'
        }).reset_index()
        
        st.table(summary)

    except Exception as e:
        st.error(f"Error: {e}")
