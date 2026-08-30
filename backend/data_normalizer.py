import pandas as pd
import numpy as np
import os
import re

def clean_currency(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r'[^\d\.\-]', '', str(val))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def parse_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d')
    # Try different string parses
    s = str(val).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return pd.to_datetime(s, format=fmt).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue
    try:
        # Fallback loose parsing
        return pd.to_datetime(s, errors='coerce').strftime('%Y-%m-%d')
    except:
        return None

def normalize_deals(filepath):
    """
    Deals Schema:
    - Deal Name
    - Owner code
    - Client Code
    - Deal Status
    - Close Date (A)
    - Closure Probability
    - Masked Deal value
    - Tentative Close Date
    - Deal Stage
    - Product deal
    - Sector/service
    - Created Date
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_excel(filepath)
    
    # Trim column names
    df.columns = [col.strip() for col in df.columns]
    
    # Handle missing essential columns
    if 'Deal Name' not in df.columns:
        df['Deal Name'] = 'Unknown Deal'
    else:
        df['Deal Name'] = df['Deal Name'].fillna('Unknown Deal').astype(str)
        
    df['Owner code'] = df['Owner code'].fillna('UNASSIGNED').astype(str)
    df['Client Code'] = df['Client Code'].fillna('UNKNOWN_CLIENT').astype(str)
    df['Deal Status'] = df['Deal Status'].fillna('Unknown').astype(str)
    
    # Normalize dates
    df['Close Date (A)'] = df['Close Date (A)'].apply(parse_date)
    df['Tentative Close Date'] = df['Tentative Close Date'].apply(parse_date)
    df['Created Date'] = df['Created Date'].apply(parse_date)
    
    # Normalize numeric columns
    df['Masked Deal value'] = df['Masked Deal value'].apply(clean_currency)
    
    # Closure Probability normalize to percentage/float
    def parse_prob(val):
        if pd.isna(val):
            return 0.0
        s = str(val).replace('%', '').strip()
        try:
            p = float(s)
            if p > 1.0:
                p = p / 100.0
            return p
        except ValueError:
            return 0.0
    df['Closure Probability'] = df['Closure Probability'].apply(parse_prob)
    
    df['Deal Stage'] = df['Deal Stage'].fillna('Lead').astype(str)
    df['Product deal'] = df['Product deal'].fillna('Not Specified').astype(str)
    df['Sector/service'] = df['Sector/service'].fillna('Other/Unspecified').astype(str)
    
    # Sector cleanup mapping (normalize naming conventions)
    sector_map = {
        'energy': 'Energy',
        'power': 'Powerline',
        'powerline': 'Powerline',
        'mining': 'Mining',
        'solar': 'Solar',
        'wind': 'Wind',
        'infrastructure': 'Infrastructure',
        'infra': 'Infrastructure',
        'agriculture': 'Agriculture',
        'agri': 'Agriculture'
    }
    def clean_sector(sec):
        sec_clean = str(sec).strip().lower()
        for k, v in sector_map.items():
            if k in sec_clean:
                return v
        return str(sec).strip()
    df['Sector/service'] = df['Sector/service'].apply(clean_sector)
    
    return df

def normalize_work_orders(filepath):
    """
    Work Orders Schema (Row 0 is headers in raw file):
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Load and set header from the first row
    df = pd.read_excel(filepath)
    # The first row contains the actual headers
    headers = list(df.iloc[0])
    # Set the remaining rows as data
    df_data = df.iloc[1:].copy()
    df_data.columns = headers
    
    # Clean column names
    df_data.columns = [str(col).strip() for col in df_data.columns]
    
    # Standardize field names and handle null values
    df_data['Deal name masked'] = df_data['Deal name masked'].fillna('Unknown Work Order').astype(str)
    df_data['Customer Name Code'] = df_data['Customer Name Code'].fillna('UNKNOWN_CUSTOMER').astype(str)
    df_data['Execution Status'] = df_data['Execution Status'].fillna('Not Started').astype(str)
    df_data['Sector'] = df_data['Sector'].fillna('Other/Unspecified').astype(str)
    
    # Handle currency columns
    currency_cols = [
        'Amount in Rupees (Excl of GST) (Masked)',
        'Amount in Rupees (Incl of GST) (Masked)',
        'Billed Value in Rupees (Excl of GST.) (Masked)',
        'Billed Value in Rupees (Incl of GST.) (Masked)',
        'Collected Amount in Rupees (Incl of GST.) (Masked)',
        'Amount to be billed in Rs. (Exl. of GST) (Masked)',
        'Amount to be billed in Rs. (Incl. of GST) (Masked)',
        'Amount Receivable (Masked)'
    ]
    for col in currency_cols:
        if col in df_data.columns:
            df_data[col] = df_data[col].apply(clean_currency)
        else:
            df_data[col] = 0.0
            
    # Handle date columns
    date_cols = [
        'Data Delivery Date', 'Date of PO/LOI', 'Probable Start Date',
        'Probable End Date', 'Last invoice date', 'Collection Date'
    ]
    for col in date_cols:
        if col in df_data.columns:
            df_data[col] = df_data[col].apply(parse_date)
        else:
            df_data[col] = None
            
    # Quantity cleanups
    def clean_qty(val):
        if pd.isna(val):
            return 0.0
        # extract digits and optional decimals
        s = str(val).upper().replace(',', '').strip()
        matches = re.findall(r'[-+]?\d*\.\d+|\d+', s)
        if matches:
            return float(matches[0])
        return 0.0
    
    qty_cols = ['Quantity by Ops', 'Quantities as per PO', 'Quantity billed (till date)', 'Balance in quantity']
    for col in qty_cols:
        if col in df_data.columns:
            df_data[col] = df_data[col].apply(clean_qty)
        else:
            df_data[col] = 0.0
            
    df_data['WO Status (billed)'] = df_data['WO Status (billed)'].fillna('Unknown').astype(str)
    df_data['Collection status'] = df_data['Collection status'].fillna('Unknown').astype(str)
    df_data['Billing Status'] = df_data['Billing Status'].fillna('Unknown').astype(str)
    
    return df_data

if __name__ == "__main__":
    deals = normalize_deals("c:/Users/rashi/OneDrive/Desktop/Skylark_drone/Deal funnel Data.xlsx")
    wos = normalize_work_orders("c:/Users/rashi/OneDrive/Desktop/Skylark_drone/Work_Order_Tracker Data.xlsx")
    print("Normalizer test success!")
    print("Deals shape:", deals.shape)
    print("Work orders shape:", wos.shape)
