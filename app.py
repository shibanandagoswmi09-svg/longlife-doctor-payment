import streamlit as st
import pandas as pd

st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")

st.title("🏥 Longlife Clinic - Doctor Payment Module")

uploaded_file = st.file_uploader("Upload Doctor Payment Excel/CSV File", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # File reading
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Column names theke extra space muche fela
        df.columns = df.columns.str.strip()

        # Calculation Function (Exact 80/85 Logic)
        def calculate_final_shares(row):
            # Column name thik ache ki na check kora, na thakle 0 dhora
            fee = row.get('Fee', 0)
            discount = row.get('Discount', 0)
            reg_fee = row.get('Reg Fee', 0)
            
            # Khali cell (NaN) thakle seta 0 kore dewa
            fee = 0 if pd.isna(fee) else fee
            discount = 0 if pd.isna(discount) else discount
            reg_fee = 0 if pd.isna(reg_fee) else reg_fee
            
            # Logic: Fee - Discount (Reg Fee asbe na)
            net_for_calc = fee - discount
            
            name = str(row.get('Doctor Name', '')).upper()
            
            # Dr. Soumya pabe 85%, baki shobai 80%
            if "SOUMYA CHATTERJEE" in name:
                doc_share = net_for_calc * 0.85
            else:
                doc_share = net_for_calc * 0.80
            
            # Clinic Share = (Net - Doc Share) + Reg Fee
            clinic_share = (net_for_calc - doc_share) + reg_fee
            
            return pd.Series([doc_share, clinic_share])

        # Error handle kore apply kora
        df[['Doc_Share_K', 'Clinic_Share_L']] = df.apply(calculate_final_shares, axis=1)

        # March ENT grouping
        march_ent_list = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
        df['Display_Name'] = df['Doctor Name'].apply(
            lambda x: "MARCH ENT" if str(x).upper() in march_ent_list else x
        )

        # Totals
        total_doc = df['Doc_Share_K'].sum()
        total_clinic = df['Clinic_Share_L'].sum()

        st.success("File Processed Successfully!")
        
        col1, col2 = st.columns(2)
        col1.metric("Total Doctor's Share", f"₹{total_doc:,.2f}")
        col2.metric("Total Clinic Share", f"₹{total_clinic:,.2f}")

        # Summary Table
        st.subheader("👨‍⚕️ Summary Report")
        summary = df.groupby('Display_Name').agg({
            'Fee': 'sum',
            'Discount': 'sum',
            'Doc_Share_K': 'sum',
            'Clinic_Share_L': 'sum'
        }).reset_index()
        
        st.dataframe(summary, use_container_width=True)

        # Full Data Preview
        with st.expander("See Detailed Row-by-Row Data"):
            st.write(df)

    except Exception as e:
        st.error(f"Error occurred: {e}")
        st.info("Check korun Excel file-er Header gulo 'Fee', 'Discount', 'Reg Fee' ebong 'Doctor Name' eivabe likha ache ki na.")
