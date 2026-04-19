import streamlit as st
import pandas as pd
from datetime import datetime

# Set up the mobile-friendly page
st.set_page_config(page_title="खाता बही", layout="centered")

# Custom CSS for Senior-Friendly Mobile UI
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input { font-size: 20px !important; padding: 10px !important;}
    label { font-size: 18px !important; font-weight: bold !important; color: #2c3e50; }
    /* Primary Save Button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #27ae60; color: white; font-size: 22px; width: 100%; padding: 12px; border-radius: 8px;
    }
    /* Secondary Add Row Button */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #3498db; color: white; font-size: 18px; width: 100%; padding: 8px; border-radius: 8px; margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.header("खाता बही (Khata Manager)")

# Initialize the memory databases
if 'khata_data' not in st.session_state:
    st.session_state.khata_data = pd.DataFrame(columns=['Date', 'Name', 'Items', 'Total Price', 'Paid', 'Balance'])

# Keep track of how many item rows to show
if 'item_count' not in st.session_state:
    st.session_state.item_count = 1

st.subheader("नया बिल बनाएं (New Bill)")

# Customer Name
name = st.text_input("ग्राहक का नाम (Customer Name)", placeholder="नाम लिखें")

st.markdown("---")
st.markdown("### सामान जोड़ें (Add Items)")

total_amount = 0.0
item_list = []

# Generate dynamic rows for items and prices
for i in range(st.session_state.item_count):
    # Using columns to put Item and Price side-by-side
    col1, col2 = st.columns(2)
    
    with col1:
        it = st.text_input(f"सामान {i+1} (Item)", key=f"item_{i}", placeholder="क्या खरीदा?")
    with col2:
        # value=None keeps it blank. format="%.2f" forces .00 at the end.
        pr = st.number_input(f"कीमत (Price - ₹)", min_value=0.0, value=None, format="%.2f", key=f"price_{i}")
    
    # Store data for calculating total
    if it:
        item_list.append(it)
    if pr is not None:
        total_amount += pr

# Button to add more item rows
if st.button("➕ एक और सामान जोड़ें (Add Another Item)", type="secondary"):
    st.session_state.item_count += 1
    st.rerun()

st.markdown("---")

# Display the Grand Total
st.markdown(f"<h3 style='color: #c0392b;'>कुल बिल (Total Amount): ₹ {total_amount:.2f}</h3>", unsafe_allow_html=True)

# Amount Paid against the total
paid = st.number_input("जमा राशि (Amount Paid - ₹)", min_value=0.0, value=None, format="%.2f")
paid_amount = paid if paid is not None else 0.0

# Calculate final balance
balance = total_amount - paid_amount

if balance > 0:
    st.error(f"बकाया (Remaining Balance): ₹ {balance:.2f}")
elif total_amount > 0 and balance == 0:
    st.success(f"पूरा भुगतान हो गया (Fully Paid): ₹ {balance:.2f}")

# Save the entire transaction
if st.button("✅ सेव करें (Save Record)", type="primary"):
    if name and item_list:
        # Combine all items into a single text line (e.g., "Shirt, Pant, Suit")
        items_str = ", ".join(item_list)
        
        new_entry = pd.DataFrame([{
            'Date': datetime.now().strftime("%d-%m-%Y"),
            'Name': name,
            'Items': items_str,
            'Total Price': total_amount,
            'Paid': paid_amount,
            'Balance': balance
        }])
        
        # Save to memory
        st.session_state.khata_data = pd.concat([new_entry, st.session_state.khata_data], ignore_index=True)
        
        # Clean up the form fields and reset rows back to 1
        st.session_state.item_count = 1
        for key in list(st.session_state.keys()):
            if key.startswith("item_") or key.startswith("price_"):
                del st.session_state[key]
                
        st.success("बिल सेव हो गया! (Bill Saved!)")
        st.rerun()
    else:
        st.warning("कृपया नाम और कम से कम एक सामान दर्ज करें! (Please enter Name and at least one Item!)")

st.divider()

# Display Past Records
st.subheader("सभी रिकॉर्ड (All Records)")

if not st.session_state.khata_data.empty:
    for index, row in st.session_state.khata_data.iterrows():
        status_icon = "🔴" if row['Balance'] > 0 else "🟢"
        
        with st.expander(f"{status_icon} {row['Date']} - {row['Name']} (बकाया: ₹{row['Balance']:.2f})"):
            st.write(f"**सामान (Items):** {row['Items']}")
            st.write(f"**कुल बिल:** ₹{row['Total Price']:.2f}")
            st.write(f"**जमा राशि:** ₹{row['Paid']:.2f}")
            
            if st.button("हटाएं (Delete)", key=f"del_{index}"):
                st.session_state.khata_data = st.session_state.khata_data.drop(index).reset_index(drop=True)
                st.rerun()
else:
    st.write("कोई रिकॉर्ड नहीं मिला। (No records found.)")
