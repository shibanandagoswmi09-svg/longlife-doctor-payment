import streamlit as st
import pandas as pd

st.set_page_config(page_title="Longlife Doctor Payment", layout="wide")
st.title("🏥 Longlife Clinic - Payment Module")

uploaded_file = st.file_uploader("Upload Updated File", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # File reading
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        df.columns = df.columns.str.strip()

        # Ebar amra group wise total ber korbo exact Excel logic-e
        # 1. Dr. Soumya Chatterjee Logic
        soumya_data = df[df['Doctor Name'].str.contains("SOUMYA", case=False, na=False)]
        soumya_net = soumya_data['Fee'].sum() - soumya_data['Discount'].sum()
        soumya_share = soumya_net * 0.85

        # 2. Baki shobai (March ENT + Others) Logic
        others_data = df[~df['Doctor Name'].str.contains("SOUMYA", case=False, na=False)]
        others_net = others_data['Fee'].sum() - others_data['Discount'].sum()
        others_share = others_net * 0.80

        # Grand Total
        grand_total_doc = soumya_share + others_share

        # Display Metrics
        st.success("File Processed!")
        col1, col2 = st.columns(2)
        col1.metric("Total Doctor's Share", f"₹{grand_total_doc:,.2f}")
        
        # Breakdown Table
        summary_data = {
            "Doctor Group": ["Dr. Soumya Chatterjee (85%)", "Other Doctors (80%)"],
            "Total Fee": [soumya_data['Fee'].sum(), others_data['Fee'].sum()],
            "Total Discount": [soumya_data['Discount'].sum(), others_data['Discount'].sum()],
            "Payable Share": [soumya_share, others_share]
        }
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)

    except Exception as e:
        st.error(f"Error: {e}")
