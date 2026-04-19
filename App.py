import streamlit as st
import pandas as pd
from datetime import datetime
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Set up the separate app page
st.set_page_config(page_title="खाता बही", layout="centered")

# Custom CSS for large, senior-friendly fonts
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input { font-size: 20px !important; padding: 10px !important;}
    label { font-size: 20px !important; font-weight: bold !important; }
    /* Style the main save button */
    div.stButton > button:first-child {
        background-color: #27ae60; color: white; font-size: 22px; width: 100%; padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.header("खाता बही (Khata Manager)")

# Initialize session state for records
if 'khata_data' not in st.session_state:
    st.session_state.khata_data = pd.DataFrame(columns=['Date', 'Name', 'Item', 'Price', 'Paid', 'Balance'])

st.subheader("नया रिकॉर्ड जोड़ें (Add Entry)")

# --- INBUILT HINDI VOICE COMPONENT ---
st.write("बोलकर लिखने के लिए नीचे दिए गए बटन को दबाएं (Tap mic to speak):")

# Create a Bokeh button that triggers the phone's native speech API
stt_button = Button(label="🎤 बोलकर सुनें", button_type="primary", width=300)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'hi-IN'; // Force Hindi language
    recognition.onresult = function (e) {
        var value = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("VOICE_TEXT", {detail: value}));
    }
    recognition.start();
"""))

# Capture the event back into Streamlit
result = streamlit_bokeh_events(
    stt_button,
    events="VOICE_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=60,
    debounce_time=0
)

# Extract the spoken text
voice_input = ""
if result and "VOICE_TEXT" in result:
    voice_input = result.get("VOICE_TEXT")
    st.success(f"सुना गया (Heard): {voice_input}")

# Data Entry Fields
name = st.text_input("ग्राहक का नाम (Name)", value=voice_input, placeholder="नाम लिखें")
item = st.text_input("सामान (Item)", placeholder="क्या खरीदा?")
    
price = st.number_input("कुल कीमत (Total Price - ₹)", min_value=0.0, step=10.0)
paid = st.number_input("जमा राशि (Amount Paid - ₹)", min_value=0.0, step=10.0)

balance = price - paid

if balance > 0:
    st.error(f"बकाया (Remaining Balance): ₹ {balance}")
else:
    st.success(f"बकाया (Remaining Balance): ₹ {balance}")

# Save Data
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
            
            if st.button("हटाएं (Delete)", key=f"del_{index}"):
                st.session_state.khata_data = st.session_state.khata_data.drop(index).reset_index(drop=True)
                st.rerun()
else:
    st.write("कोई रिकॉर्ड नहीं मिला। (No records found.)")
