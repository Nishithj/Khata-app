import streamlit as st
import pandas as pd
from datetime import datetime

# Set up the separate app page
st.set_page_config(page_title="खाता बही", layout="centered")

# Custom CSS for Senior-Friendly Mobile UI
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input { font-size: 20px !important; padding: 10px !important;}
    label { font-size: 20px !important; font-weight: bold !important; }
    div.stButton > button:first-child {
        background-color: #27ae60; color: white; font-size: 22px; width: 100%; padding: 10px; border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.header("खाता बही (Khata Manager)")

# Create temporary storage in the app's memory
if 'khata_data' not in st.session_state:
    st.session_state.khata_data = pd.DataFrame(columns=['Date', 'Name', 'Item', 'Price', 'Paid', 'Balance'])

st.subheader("नया रिकॉर्ड जोड़ें (Add Entry)")

st.info("💡 **टिप (Tip):** बोलकर लिखने के लिए अपने मोबाइल कीबोर्ड के माइक (🎤) का उपयोग करें।")

# Input Fields
name = st.text_input("ग्राहक का नाम (Name)", placeholder="नाम लिखें")
item = st.text_input("सामान (Item)", placeholder="क्या खरीदा?")
price = st.number_input("कुल कीमत (Total Price - ₹)", min_value=0.0, step=10.0)
paid = st.number_input("जमा राशि (Amount Paid - ₹)", min_value=0.0, step=10.0)
balance = price - paid

if balance > 0:
    st.error(f"बकाया (Remaining Balance): ₹ {balance}")
else:
    st.success(f"बकाया (Remaining Balance): ₹ {balance}")

# Save Data to Memory
if st.button("सेव करें (Save)"):
    if name and item:
        new_entry = pd.DataFrame([{
            'Date': datetime.now().strftime("%d-%m-%Y"),
            'Name': name,
            'Item': item,
            'Price': price,
            'Paid': paid,
            'Balance': balance
        }])
        
        # Add new entry to the top of the list
        st.session_state.khata_data = pd.concat([new_entry, st.session_state.khata_data], ignore_index=True)
        st.success("रिकॉर्ड सेव हो गया! (Record Saved!)")
        st.rerun()
    else:
        st.warning("कृपया नाम और सामान दर्ज करें! (Please enter Name and Item!)")

st.divider()

# Display Records
st.subheader("सभी रिकॉर्ड (All Records)")

if not st.session_state.khata_data.empty:
    for index, row in st.session_state.khata_data.iterrows():
        status_icon = "🔴" if row['Balance'] > 0 else "🟢"
        
        with st.expander(f"{status_icon} {row['Date']} - {row['Name']} (बकाया: ₹{row['Balance']})"):
            st.write(f"**सामान (Item):** {row['Item']}")
            st.write(f"**कुल कीमत:** ₹{row['Price']}")
            st.write(f"**जमा राशि:** ₹{row['Paid']}")
            
            # Delete record button
            if st.button("हटाएं (Delete)", key=f"del_{index}"):
                st.session_state.khata_data = st.session_state.khata_data.drop(index).reset_index(drop=True)
                st.rerun()
else:
    st.write("कोई रिकॉर्ड नहीं मिला। (No records found.)")
