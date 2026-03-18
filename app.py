import streamlit as st
import pandas as pd

st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")

st.title("🏥 Longlife Clinic - Final Payment Module")

uploaded_file = st.file_uploader("Upload File", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # File Load
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 1. CLEANING: Column name ebong Data theke extra space muche fela
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        def calculate_logic(row):
            # Numeric conversion ensure kora
            try:
                fee = pd.to_numeric(row.get('Fee', 0), errors='coerce')
                discount = pd.to_numeric(row.get('Discount', 0), errors='coerce')
                reg_fee = pd.to_numeric(row.get('Reg Fee', 0), errors='coerce')
            except:
                fee, discount, reg_fee = 0, 0, 0
            
            # NaN hole 0 kora
            fee = 0 if pd.isna(fee) else fee
            discount = 0 if pd.isna(discount) else discount
            reg_fee = 0 if pd.isna(reg_fee) else reg_fee

            # BASE CALCULATION: (Fee - Discount)
            net_for_calc = fee - discount
            
            # NAME CHECK: Soumya Chatterjee-er spelling variations handle kora
            full_name = str(row.get('Doctor Name', '')).upper()
            
            if "SOUMYA" in full_name and "CHATTERJEE" in full_name:
                doc_share = net_for_calc * 0.85
            else:
                doc_share = net_for_calc * 0.80
            
            clinic_share = (net_for_calc - doc_share) + reg_fee
            return pd.Series([doc_share, clinic_share])

        # Apply logic
        df[['Doc_Share_K', 'Clinic_Share_L']] = df.apply(calculate_logic, axis=1)

        # Totals
        total_doc = df['Doc_Share_K'].sum()
        
        # Result Display (Rounding to 0 decimal places to match manual total)
        st.metric("Total Doctor's Share", f"₹{round(total_doc):,}")

        # Summary for Verification
        march_ent_list = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
        df['Group'] = df['Doctor Name'].apply(lambda x: "MARCH ENT" if str(x).upper() in march_ent_list else x)
        
        summary = df.groupby('Group').agg({'Doc_Share_K': 'sum'}).reset_index()
        st.table(summary)

    except Exception as e:
        st.error(f"Error: {e}")
