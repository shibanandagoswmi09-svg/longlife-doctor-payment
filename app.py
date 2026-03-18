import streamlit as st
import pandas as pd

st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")
st.title("🏥 Longlife Clinic - Payment Module")

uploaded_file = st.file_uploader("Upload Updated File", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        def calculate_share(row):
            # STRICT LOGIC: Fee theke Discount bad diye Net Calculation
            net_val = float(row.get('Fee', 0)) - float(row.get('Discount', 0))
            name = str(row.get('Doctor Name', '')).upper()
            
            # Dr. Soumya 85%, Baki shobai 80%
            percentage = 0.85 if "SOUMYA" in name else 0.80
            
            # Rounding to 0 decimal to match manual manual calculation
            return round(net_val * percentage)

        df['Doctor_Payable'] = df.apply(calculate_share, axis=1)
        
        total_payment = df['Doctor_Payable'].sum()
        
        st.success("File Processed!")
        st.metric("Total Doctor's Share", f"₹{total_payment:,}")

        # Group Summary
        march_ent_list = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
        df['Group'] = df['Doctor Name'].apply(lambda x: "MARCH ENT" if str(x).upper() in march_ent_list else x)
        
        summary = df.groupby('Group')['Doctor_Payable'].sum().reset_index()
        st.table(summary)

    except Exception as e:
        st.error(f"Error: {e}")
