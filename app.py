import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Doctor Payment Dashboard", layout="wide")
st.title("🏥 Longlife Clinic - Doctor Payment Module")

uploaded_file = st.file_uploader("Upload File", type=['csv', 'xlsx'])

if uploaded_file:

    # ---------------- READ FILE ----------------
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Clean columns
    df.columns = df.columns.str.strip().str.upper()

    st.write("Columns detected:", df.columns)

    # ---------------- SAFE FLOAT ----------------
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0

    # ---------------- PAYMENT LOGIC ----------------
    def calculate_payment(row):

        fee = safe_float(row.get('FEE'))
        discount = safe_float(row.get('DISCOUNT'))
        reg_fee = safe_float(row.get('REG FEE'))

        # ✅ IMPORTANT: Use NET AMOUNT FIRST (matches real billing)
        net = safe_float(row.get('NET AMOUNT'))

        # fallback if missing
        if net == 0:
            net = fee - discount

        # Clean doctor name
        name = str(row.get('DOCTOR NAME', '')).upper().replace('.', '').strip()

        # ✅ Doctor Share Rule
        if "SOUMYA CHATTERJEE" in name:
            doc_share = net * 0.85
        else:
            doc_share = net * 0.80

        # ✅ Clinic Share Rule
        clinic_share = (net - doc_share) + reg_fee

        # ✅ IMPORTANT: ROUNDING (to match Excel)
        doc_share = round(doc_share, 0)
        clinic_share = round(clinic_share, 0)

        return pd.Series([doc_share, clinic_share])

    # Apply calculation
    df[['DOC_SHARE', 'CLINIC_SHARE']] = df.apply(calculate_payment, axis=1)

    # ---------------- KPI ----------------
    total_doc = df['DOC_SHARE'].sum()
    total_clinic = df['CLINIC_SHARE'].sum()

    st.markdown("## 📊 Summary")
    col1, col2 = st.columns(2)

    col1.metric("💰 Doctor Payment", f"₹{total_doc:,.0f}")
    col2.metric("🏥 Clinic Share", f"₹{total_clinic:,.0f}")

    # ---------------- DOCTOR SUMMARY ----------------
    st.markdown("## 👨‍⚕️ Doctor Wise Payment")

    summary = df.groupby('DOCTOR NAME').agg({
        'DOC_SHARE': 'sum',
        'CLINIC_SHARE': 'sum'
    }).reset_index()

    summary.columns = ['Doctor', 'Doctor Payment', 'Clinic Share']

    st.dataframe(summary)

    # ---------------- ERROR CHECK (VERY IMPORTANT) ----------------
    st.markdown("## 🧠 Audit Check")

    df['EXPECTED_NET'] = df['FEE'] - df['DISCOUNT']
    df['DIFF'] = df['NET AMOUNT'] - df['EXPECTED_NET']

    mismatch = df[df['DIFF'] != 0]

    if not mismatch.empty:
        st.warning("⚠️ Some rows have mismatch between Net Amount and Fee-Discount")
        st.dataframe(mismatch[['DOCTOR NAME', 'FEE', 'DISCOUNT', 'NET AMOUNT', 'DIFF']])
    else:
        st.success("✅ No mismatch found. Data is consistent.")

    # ---------------- DOWNLOAD ----------------
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Full Data', index=False)
    summary.to_excel(writer, sheet_name='Summary', index=False)

    writer.close()

    st.download_button(
        label="⬇️ Download Report",
        data=output.getvalue(),
        file_name="Doctor_Payment_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------- RAW DATA ----------------
    with st.expander("🔍 View Full Data"):
        st.dataframe(df)
