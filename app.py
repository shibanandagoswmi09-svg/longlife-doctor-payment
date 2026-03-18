import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")

st.title("🏥 Longlife Clinic - Doctor Payment Module")
st.write("Excel file upload korun ebong automatic payment summary dekhun.")

# File uploader
uploaded_file = st.file_uploader("Upload Doctor Payment File (Excel/CSV)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # File reading logic
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Column names theke extra space remove kora (Standardization)
        df.columns = df.columns.str.strip()

        # Calculation Logic function
        def calculate_payment(row):
            # Header miss hole 0 dhorbe (Error avoid korar jonno)
            fee = float(row.get('Fee', 0)) if pd.notna(row.get('Fee')) else 0
            discount = float(row.get('Discount', 0)) if pd.notna(row.get('Discount')) else 0
            reg_fee = float(row.get('Reg Fee', 0)) if pd.notna(row.get('Reg Fee')) else 0
            
            # AMADER LOGIC: Base Amount = Fee - Discount (Reg Fee asbe na)
            # Eta kora holo karon Excel-er 'Net Amount' column-e vul thakte pare
            net_for_calc = fee - discount
            
            name = str(row.get('Doctor Name', '')).upper()
            
            # 1. Dr. Soumya Chatterjee paben 85%
            if "SOUMYA CHATTERJEE" in name:
                doc_share = net_for_calc * 0.85
            # 2. Baki shobai (March ENT shoho) paben 80%
            else:
                doc_share = net_for_calc * 0.80
            
            # Clinic Share Logic: (Net - Doc Share) + Reg Fee
            clinic_share = (net_for_calc - doc_share) + reg_fee
            
            return pd.Series([doc_share, clinic_share])

        # New columns toiri kora
        df[['Doc_Share_K', 'Clinic_Share_L']] = df.apply(calculate_payment, axis=1)

        # March ENT Grouping
        march_ent_docs = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
        df['Group_Name'] = df['Doctor Name'].apply(
            lambda x: "MARCH ENT" if str(x).upper() in march_ent_docs else x
        )

        # --- Display Results ---
        total_doc_share = df['Doc_Share_K'].sum()
        total_clinic_share = df['Clinic_Share_L'].sum()

        st.markdown("---")
        col1, col2 = st.columns(2)
        col1.metric("Total Doctor's Share", f"₹{total_doc_share:,.2f}")
        col2.metric("Total Clinic Share", f"₹{total_clinic_share:,.2f}")

        # Summary Table for Doctors
        st.subheader("👨‍⚕️ Category Wise Summary")
        summary = df.groupby('Group_Name').agg({
            'Fee': 'sum',
            'Discount': 'sum',
            'Doc_Share_K': 'sum',
            'Clinic_Share_L': 'sum'
        }).reset_index()
        
        # Table column rename for better look
        summary.columns = ['Doctor/Group Name', 'Total Fee', 'Total Discount', 'Doc Share (Payable)', 'Clinic Share']
        st.table(summary)

        # Full Data Preview
        with st.expander("Click here to see detailed Row-by-Row calculation"):
            st.dataframe(df)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Processed Report", csv, "longlife_payment_report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Ensure your file has 'Doctor Name', 'Fee', 'Reg Fee', and 'Discount' columns.")
