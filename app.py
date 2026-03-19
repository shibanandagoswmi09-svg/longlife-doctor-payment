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

    # Clean column names
    df.columns = df.columns.str.strip().str.upper()
    st.write("✅ Columns detected:", df.columns)

    # ---------------- SAFE FLOAT ----------------
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0

    # ---------------- CURRENT CALCULATION ----------------
    def calculate_payment(row):

        net = safe_float(row.get('NET AMOUNT'))
        reg_fee = safe_float(row.get('REG FEE'))

        name = str(row.get('DOCTOR NAME', '')).upper().replace('.', '').strip()

        if "SOUMYA CHATTERJEE" in name:
            doc_share = net * 0.85
        else:
            doc_share = net * 0.80

        clinic_share = (net - doc_share) + reg_fee

        return pd.Series([round(doc_share, 0), round(clinic_share, 0)])

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

    summary = df.groupby('DOCTOR NAME')['DOC_SHARE'].sum().reset_index()
    summary.columns = ['Doctor', 'Doctor Payment']

    st.dataframe(summary)

    # ======================================================
    # 🔍 MISMATCH DETECTION (IMPORTANT DEBUG PART)
    # ======================================================

    st.markdown("## 🚨 Mismatch Detection")

    def detect_mismatch(row):
        fee = safe_float(row.get('FEE'))
        discount = safe_float(row.get('DISCOUNT'))
        net = safe_float(row.get('NET AMOUNT'))

        name = str(row.get('DOCTOR NAME', '')).upper()
        pct = 0.85 if "SOUMYA CHATTERJEE" in name else 0.80

        calc_net = net * pct
        calc_fee = (fee - discount) * pct

        return pd.Series([
            round(calc_net, 2),
            round(calc_fee, 2),
            round(calc_net - calc_fee, 2)
        ])

    df[['FROM_NET', 'FROM_FEE_DISC', 'DIFFERENCE']] = df.apply(detect_mismatch, axis=1)

    mismatch_rows = df[df['DIFFERENCE'] != 0]

    if not mismatch_rows.empty:
        st.error(f"⚠️ Found {len(mismatch_rows)} mismatch rows")
        st.dataframe(
            mismatch_rows[['DOCTOR NAME','FEE','DISCOUNT','NET AMOUNT','FROM_NET','FROM_FEE_DISC','DIFFERENCE']]
        )
    else:
        st.success("✅ No mismatch rows found")

    # ---------------- DOWNLOAD ----------------
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
