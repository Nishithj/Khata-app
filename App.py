import streamlit as st
import pandas as pd
from datetime import datetime
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from supabase import create_client, Client

# Set up the separate app page
st.set_page_config(page_title="खाता बही", layout="centered")

# Initialize Supabase client
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Custom CSS
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input { font-size: 20px !important; padding: 10px !important;}
    label { font-size: 20px !important; font-weight: bold !important; }
    div.stButton > button:first-child {
        background-color: #27ae60; color: white; font-size: 22px; width: 100%; padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.header("खाता बही (Khata Manager)")
st.subheader("नया रिकॉर्ड जोड़ें (Add Entry)")

# Voice Input Component
st.write("बोलकर लिखने के लिए नीचे दिए गए बटन को दबाएं (Tap mic to speak):")
stt_button = Button(label="🎤 बोलकर सुनें", button_type="primary", width=300)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'hi-IN';
    recognition.onresult = function (e) {
        var value = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("VOICE_TEXT", {detail: value}));
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button, events="VOICE_TEXT", key="listen", refresh_on_update=False, override_height=60, debounce_time=0
)

voice_input = ""
if result and "VOICE_TEXT" in result:
    voice_input = result.get("VOICE_TEXT")
    st.success(f"सुना गया (Heard): {voice_input}")

# Input Fields
name = st.text_input("ग्राहक का नाम (Name)", value=voice_input, placeholder="नाम लिखें")
item = st.text_input("सामान (Item)", placeholder="क्या खरीदा?")
price = st.number_input("कुल कीमत (Total Price - ₹)", min_value=0.0, step=10.0)
paid = st.number_input("जमा राशि (Amount Paid - ₹)", min_value=0.0, step=10.0)
balance = price - paid

if balance > 0:
    st.error(f"बकाया (Remaining Balance): ₹ {balance}")
else:
    st.success(f"बकाया (Remaining Balance): ₹ {balance}")

# Save Data to Supabase
if st.button("सेव करें (Save)"):
    if name and item:
        data = {
            "date": datetime.now().strftime("%d-%m-%Y"),
            "name": name,
            "item": item,
            "price": price,
            "paid": paid,
            "balance": balance
        }
        # Insert into Supabase
        supabase.table("khata_records").insert(data).execute()
        st.success("रिकॉर्ड सेव हो गया! (Record Saved to Cloud!)")
        st.rerun()
    else:
        st.warning("कृपया नाम और सामान दर्ज करें! (Please enter Name and Item!)")

st.divider()

# Fetch and Display Records from Supabase
st.subheader("सभी रिकॉर्ड (All Records)")

response = supabase.table("khata_records").select("*").order("id", desc=True).execute()
records = response.data

if records:
    for row in records:
        status_icon = "🔴" if row['balance'] > 0 else "🟢"
        with st.expander(f"{status_icon} {row['date']} - {row['name']} (बकाया: ₹{row['balance']})"):
            st.write(f"**सामान (Item):** {row['item']}")
            st.write(f"**कुल कीमत:** ₹{row['price']}")
            st.write(f"**जमा राशि:** ₹{row['paid']}")
            
            # Delete record
            if st.button("हटाएं (Delete)", key=f"del_{row['id']}"):
                supabase.table("khata_records").delete().eq("id", row['id']).execute()
                st.rerun()
else:
    st.write("कोई रिकॉर्ड नहीं मिला। (No records found.)")
