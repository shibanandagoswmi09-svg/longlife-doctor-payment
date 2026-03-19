import streamlit as st
import pandas as pd
import io

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Doctor Payment Dashboard", layout="wide")
st.title("🏥 Longlife Clinic - Doctor Payment Module")

uploaded_file = st.file_uploader("📂 Upload File (Excel/CSV)", type=['csv', 'xlsx'])

if uploaded_file:

    # ---------------- READ FILE ----------------
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Clean columns
    df.columns = df.columns.str.strip().str.upper()
    st.write("✅ Columns detected:", df.columns)

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
        net = safe_float(row.get('NET AMOUNT'))

        # Fallback if Net missing
        if net == 0:
            net = fee - discount

        # ✅ FIX: Remove Reg Fee from Net (avoid double count)
        base_amount = net - reg_fee

        # Safety check
        if base_amount <= 0:
            base_amount = net

        # Clean doctor name
        name = str(row.get('DOCTOR NAME', '')).upper().replace('.', '').strip()

        # Doctor share logic
        if "SOUMYA CHATTERJEE" in name:
            doc_share = base_amount * 0.85
        else:
            doc_share = base_amount * 0.80

        # Clinic share
        clinic_share = (base_amount - doc_share) + reg_fee

        # Rounding (important)
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
    col1.metric("💰 Total Doctor Payment", f"₹{total_doc:,.0f}")
    col2.metric("🏥 Total Clinic Share", f"₹{total_clinic:,.0f}")

    # ---------------- DOCTOR SUMMARY ----------------
    st.markdown("## 👨‍⚕️ Doctor-wise Payment")

    summary = df.groupby('DOCTOR NAME').agg({
        'DOC_SHARE': 'sum',
        'CLINIC_SHARE': 'sum'
    }).reset_index()

    summary.columns = ['Doctor', 'Doctor Payment', 'Clinic Share']

    st.dataframe(summary)

    # ---------------- AUDIT CHECK ----------------
    st.markdown("## 🧠 Audit Check")

    df['EXPECTED_NET'] = df['FEE'] - df['DISCOUNT']
    df['DIFF'] = df['NET AMOUNT'] - df['EXPECTED_NET']

    mismatch = df[df['DIFF'] != 0]

    if not mismatch.empty:
        st.warning("⚠️ Some rows have mismatch (Net Amount vs Fee-Discount)")
        st.dataframe(mismatch[['DOCTOR NAME', 'FEE', 'DISCOUNT', 'REG FEE', 'NET AMOUNT', 'DIFF']])
    else:
        st.success("✅ Data is consistent")

    # ---------------- DOWNLOAD EXCEL ----------------
    st.markdown("## 📥 Download Report")

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Full Data', index=False)
    summary.to_excel(writer, sheet_name='Summary', index=False)

    writer.close()

    st.download_button(
        label="⬇️ Download Excel Report",
        data=output.getvalue(),
        file_name="Doctor_Payment_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------- RAW DATA ----------------
    with st.expander("🔍 View Full Data"):
        st.dataframe(df)
