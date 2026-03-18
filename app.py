import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doctor Payment Calculator", layout="wide")

st.title("🩺 Clinic Doctor Payment Module")
st.write("Upload the Excel/CSV file to calculate payments based on your logic.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # --- Calculation Logic ---
    
    # 1. Net Amount for Calculation (J) = Fee - Discount
    df['Net_Amount_J'] = df['Fee'] - df['Discount']

    # 2. Doctor's Share (K)
    def calculate_dr_share(row):
        name = str(row['Doctor Name']).upper()
        net = row['Net_Amount_J']
        
        # Dr. Soumya Chatterjee gets 85%
        if "SOUMYA CHATTERJEE" in name:
            return net * 0.85
        # Everyone else (including March ENT) gets 80%
        else:
            return net * 0.80

    df['Doctor_Share_K'] = df.apply(calculate_dr_share, axis=1)

    # 3. Clinic Share (L) = (Net - Doc Share) + Reg Fee
    df['Clinic_Share_L'] = df['Net_Amount_J'] - df['Doctor_Share_K'] + df['Reg Fee']

    # --- Grouping for "March ENT" ---
    march_ent_docs = ['DR. ARJUN DASGUPTA', 'DR. CHIRAJIT DUTTA', 'DR. NVK MOHAN']
    df['Display_Name'] = df['Doctor Name'].apply(
        lambda x: "MARCH ENT" if str(x).upper() in march_ent_docs else x
    )

    # --- Display Results ---
    st.subheader("Detailed Calculation Table")
    st.write(df[['Date', 'Doctor Name', 'Fee', 'Reg Fee', 'Discount', 'Net_Amount_J', 'Doctor_Share_K', 'Clinic_Share_L']])

    # --- Summary Table ---
    st.subheader("Final Summary Report")
    summary = df.groupby('Display_Name').agg({
        'Net_Amount_J': 'sum',
        'Doctor_Share_K': 'sum',
        'Clinic_Share_L': 'sum'
    }).reset_index()

    # Grand Total
    total_doc_pay = df['Doctor_Share_K'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Doctor's Share", f"₹{total_doc_pay:,.2f}")
    col2.metric("Total Clinic Share", f"₹{df['Clinic_Share_L'].sum():,.2f}")

    st.table(summary)

    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Processed File", csv, "doctor_payment_report.csv", "text/csv")
