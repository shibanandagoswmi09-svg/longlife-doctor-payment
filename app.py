def calculate_final_shares(row):
    fee = row['Fee']
    discount = row['Discount']
    reg_fee = row['Reg Fee']
    
    # Calculation base: Fee theke discount bad, Reg Fee ekhane asbe na
    net_for_calc = fee - discount
    
    name = str(row['Doctor Name']).upper()
    
    # 1. Dr. Soumya Chatterjee (85%)
    if "SOUMYA CHATTERJEE" in name:
        doc_share = net_for_calc * 0.85
    # 2. Baki shobai (March ENT + Others) (80%)
    else:
        doc_share = net_for_calc * 0.80
        
    # Clinic Share logic: Calculation net theke doc share bad + full Reg Fee
    clinic_share = (net_for_calc - doc_share) + reg_fee
    
    return pd.Series([doc_share, clinic_share])

# Apply kora hochhe
df[['Doc_Share_K', 'Clinic_Share_L']] = df.apply(calculate_final_shares, axis=1)
