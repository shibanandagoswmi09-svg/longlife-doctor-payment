import streamlit as st
import pandas as pd
import io

# Page setup
st.set_page_config(page_title="Doctor Payment Dashboard", layout="wide")

st.title("🏥 Longlife Clinic - Smart Payment Dashboard")

uploaded_file = st.file_uploader("📂 Upload Doctor Payment File", type=['csv', 'xlsx'])

if uploaded_file:

    # ------------------ READ FILE ------------------
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Clean columns
    df.columns = df.columns.str.strip().str.upper()

    st.write("✅ Columns detected:", df.columns)

    # ------------------ SAFE FLOAT ------------------
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0

    # ------------------ DATE FILTER ------------------
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

        selected_month = st.selectbox(
            "📅 Select Month",
            df['DATE'].dt.to_period('M').astype(str).unique()
        )

        df = df[df['DATE'].dt.to_period('M').astype(str) == selected_month]

    # ------------------ CALCULATION ------------------
    def calculate_payment(row):
        fee = safe_float(row.get('FEE'))
        discount = safe_float(row.get('DISCOUNT'))
        reg_fee = safe_float(row.get('REG FEE'))

        net = safe_float(row.get('NET AMOUNT'))
        if net == 0:
            net = fee - discount

        name = str(row.get('DOCTOR NAME', '')).upper().replace('.', '').strip()

        # Condition
        if "SOUMYA CHATTERJEE" in name:
            doc_share = net * 0.85
        else:
            doc_share = net * 0.80

        clinic_share = (net - doc_share) + reg_fee

        return pd.Series([doc_share, clinic_share])

    df[['DOC_SHARE', 'CLINIC_SHARE']] = df.apply(calculate_payment, axis=1)

    # ------------------ KPI ------------------
    total_doc = df['DOC_SHARE'].sum()
    total_clinic = df['CLINIC_SHARE'].sum()
    total_revenue = df['DOC_SHARE'].sum() + df['CLINIC_SHARE'].sum()

    st.markdown("## 📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Doctor Payout", f"₹{total_doc:,.0f}")
    col2.metric("🏥 Clinic Earnings", f"₹{total_clinic:,.0f}")
    col3.metric("📈 Total Revenue", f"₹{total_revenue:,.0f}")

    # ------------------ SUMMARY ------------------
    st.markdown("## 👨‍⚕️ Doctor Summary")

    summary = df.groupby('DOCTOR NAME').agg({
        'FEE': 'sum',
        'DISCOUNT': 'sum',
        'DOC_SHARE': 'sum',
        'CLINIC_SHARE': 'sum'
    }).reset_index()

    summary.columns = ['Doctor', 'Total Fee', 'Discount', 'Doctor Pay', 'Clinic Earn']

    st.dataframe(summary)

    # ------------------ CHART ------------------
    st.markdown("## 📊 Earnings Chart")

    st.bar_chart(summary.set_index('Doctor')[['Doctor Pay', 'Clinic Earn']])

    # ------------------ EXPORT MULTI-SHEET ------------------
    st.markdown("## 📥 Download Reports")

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Main sheet
    df.to_excel(writer, sheet_name='Full Data', index=False)

    # Doctor-wise sheets
    for doctor in df['DOCTOR NAME'].unique():
        doc_df = df[df['DOCTOR NAME'] == doctor]
        sheet_name = doctor[:30]  # Excel limit
        doc_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Summary sheet
    summary.to_excel(writer, sheet_name='Summary', index=False)

    writer.close()

    st.download_button(
        label="⬇️ Download Full Excel Report",
        data=output.getvalue(),
        file_name="Doctor_Payment_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ------------------ RAW DATA ------------------
    with st.expander("🔍 View Full Data"):
        st.dataframe(df)
