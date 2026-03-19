import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Doctor Payment Dashboard", layout="wide")
st.title("🏥 Longlife Clinic - Doctor Payment Module")

uploaded_file = st.file_uploader("📂 Upload File", type=['csv', 'xlsx'])

if uploaded_file:

    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip().str.upper()

    def safe_float(val):
        try:
            return float(val)
        except:
            return 0

    # ✅ FINAL LOGIC
    def calculate_payment(row):

        net = safe_float(row.get('NET AMOUNT'))
        reg_fee = safe_float(row.get('REG FEE'))

        name = str(row.get('DOCTOR NAME', '')).upper().replace('.', '').strip()

        # Doctor %
        if "SOUMYA CHATTERJEE" in name:
            doc_share = net * 0.85
        else:
            doc_share = net * 0.80

        clinic_share = (net - doc_share) + reg_fee

        # rounding
        doc_share = round(doc_share, 0)
        clinic_share = round(clinic_share, 0)

        return pd.Series([doc_share, clinic_share])

    df[['DOC_SHARE', 'CLINIC_SHARE']] = df.apply(calculate_payment, axis=1)

    # KPI
    total_doc = df['DOC_SHARE'].sum()
    total_clinic = df['CLINIC_SHARE'].sum()

    st.metric("💰 Total Doctor Payment", f"₹{total_doc:,.0f}")
    st.metric("🏥 Clinic Share", f"₹{total_clinic:,.0f}")

    # Summary
    summary = df.groupby('DOCTOR NAME')['DOC_SHARE'].sum().reset_index()
    summary.columns = ['Doctor', 'Doctor Payment']

    st.dataframe(summary)

    # Download
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Full Data', index=False)
    summary.to_excel(writer, sheet_name='Summary', index=False)

    writer.close()

    st.download_button(
        "⬇️ Download Report",
        data=output.getvalue(),
        file_name="Doctor_Payment_Report.xlsx"
    )
