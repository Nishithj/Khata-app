import streamlit as st
from datetime import datetime

# Set up the mobile-friendly page
st.set_page_config(page_title="खाता बही", layout="centered")

# --- CUSTOM CSS FOR SENIOR CITIZENS ---
st.markdown("""
    <style>
    /* Make input boxes massive and easy to tap */
    .stTextInput input, .stNumberInput input { 
        font-size: 24px !important; 
        padding: 15px !important;
        border: 2px solid #bdc3c7 !important;
        border-radius: 8px !important;
    }
    /* Make labels large and bold */
    label { font-size: 20px !important; font-weight: bold !important; color: #2c3e50; }
    
    /* Primary Save Button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #27ae60; color: white; font-size: 24px; width: 100%; padding: 15px; border-radius: 8px; font-weight: bold;
    }
    /* Category Add Buttons */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #f39c12; color: white; font-size: 18px; padding: 10px; border-radius: 8px; margin-bottom: 10px;
    }
    /* Distinguish sections */
    .category-header { background-color: #ecf0f1; padding: 10px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM MEMORY SETUP ---
if 'bills' not in st.session_state: st.session_state.bills = []
if 'bill_counter' not in st.session_state: st.session_state.bill_counter = 1
if 'g_cnt' not in st.session_state: st.session_state.g_cnt = 1
if 's_cnt' not in st.session_state: st.session_state.s_cnt = 1
if 'c_cnt' not in st.session_state: st.session_state.c_cnt = 1

st.header("📖 खाता बही (Ledger)")

# Voice Tip
st.info("💡 **टिप:** बोलकर लिखने के लिए अपने मोबाइल कीबोर्ड के माइक (🎤) का उपयोग करें।")

st.divider()

# --- BILL HEADER ---
current_date = datetime.now()
st.markdown(f"### 📝 बिल नंबर (Bill No): **{st.session_state.bill_counter}**")
st.markdown(f"### 📅 तारीख (Date): **{current_date.strftime('%d-%m-%Y')}**")

st.markdown("---")

# --- PARTY DETAILS ---
party = st.text_input("ग्राहक का नाम (Party Name) *", key="party", placeholder="नाम लिखें")
father = st.text_input("पिता का नाम (Father Name)", key="father", placeholder="(Optional)")
addr = st.text_input("पता (Address)", key="addr", placeholder="(Optional)")
num = st.text_input("मोबाइल नंबर (Number)", key="num", placeholder="(Optional)")

total_bill_value = 0.0

# --- 🥇 GOLD SECTION ---
st.markdown("<div class='category-header'><h3>🥇 सोने का सामान (Gold)</h3></div>", unsafe_allow_html=True)
gold_items = []
for i in range(st.session_state.g_cnt):
    g_name = st.text_input(f"सामान का नाम (Item Name)", key=f"g_name_{i}")
    c1, c2 = st.columns(2)
    with c1: g_rate = st.number_input(f"भाव (Rate)", value=None, format="%.2f", key=f"g_rate_{i}")
    with c2: g_wt = st.number_input(f"वजन (Weight)", value=None, format="%.2f", key=f"g_wt_{i}")
    
    g_price = st.number_input(f"कुल कीमत (Price - ₹)", value=None, format="%.2f", key=f"g_price_{i}")
    
    if g_name or g_price:
        gold_items.append({"name": g_name, "rate": g_rate, "wt": g_wt, "price": g_price})
        if g_price: total_bill_value += g_price

if st.button("➕ सोना और जोड़ें (Add More Gold)"): 
    st.session_state.g_cnt += 1
    st.rerun()

# --- 🥈 SILVER SECTION ---
st.markdown("<div class='category-header'><h3>🥈 चांदी का सामान (Silver)</h3></div>", unsafe_allow_html=True)
silver_items = []
for i in range(st.session_state.s_cnt):
    s_name = st.text_input(f"सामान का नाम (Item Name)", key=f"s_name_{i}")
    c1, c2 = st.columns(2)
    with c1: s_rate = st.number_input(f"भाव (Rate)", value=None, format="%.2f", key=f"s_rate_{i}")
    with c2: s_wt = st.number_input(f"वजन (Weight)", value=None, format="%.2f", key=f"s_wt_{i}")
    
    s_price = st.number_input(f"कुल कीमत (Price - ₹)", value=None, format="%.2f", key=f"s_price_{i}")
    
    if s_name or s_price:
        silver_items.append({"name": s_name, "rate": s_rate, "wt": s_wt, "price": s_price})
        if s_price: total_bill_value += s_price

if st.button("➕ चांदी और जोड़ें (Add More Silver)"): 
    st.session_state.s_cnt += 1
    st.rerun()

# --- 👕 CLOTH SECTION ---
st.markdown("<div class='category-header'><h3>👕 कपड़े का सामान (Cloth)</h3></div>", unsafe_allow_html=True)
cloth_items = []
for i in range(st.session_state.c_cnt):
    c_name = st.text_input(f"सामान का नाम (Item Name)", key=f"c_name_{i}")
    c_rate = st.number_input(f"भाव/कीमत (Rate/Price - ₹)", value=None, format="%.2f", key=f"c_rate_{i}")
    
    if c_name or c_rate:
        cloth_items.append({"name": c_name, "rate": c_rate})
        if c_rate: total_bill_value += c_rate

if st.button("➕ कपड़ा और जोड़ें (Add More Cloth)"): 
    st.session_state.c_cnt += 1
    st.rerun()

st.markdown("---")

# --- GRAND TOTAL & PAYMENT ---
st.markdown(f"<h2 style='color: #c0392b; text-align: center;'>कुल बिल (Total Value): ₹ {total_bill_value:.2f}</h2>", unsafe_allow_html=True)

paid = st.number_input("आज की जमा राशि (Amount Paid - ₹)", min_value=0.0, value=None, format="%.2f", key="paid")
paid_amt = paid if paid else 0.0
balance = total_bill_value - paid_amt

if balance > 0:
    st.error(f"बकाया (Remaining Balance): ₹ {balance:.2f}")
elif total_bill_value > 0 and balance == 0:
    st.success(f"पूरा भुगतान हो गया (Fully Paid)")

# --- SAVE BILL LOGIC ---
if st.button("✅ बिल सेव करें (Save Bill)", type="primary"):
    if not party:
        st.warning("कृपया ग्राहक का नाम दर्ज करें! (Please enter Party Name)")
    else:
        new_bill = {
            "bill_no": st.session_state.bill_counter,
            "date": current_date,
            "party": party,
            "father": father,
            "addr": addr,
            "num": num,
            "gold": gold_items,
            "silver": silver_items,
            "cloth": cloth_items,
            "total": total_bill_value,
            "paid": paid_amt,
            "balance": balance
        }
        
        # Add to records and increment counter
        st.session_state.bills.insert(0, new_bill)
        st.session_state.bill_counter += 1
        
        # Reset counters back to 1
        st.session_state.g_cnt = 1
        st.session_state.s_cnt = 1
        st.session_state.c_cnt = 1
        
        # Clear all input boxes
        for key in list(st.session_state.keys()):
            if key.startswith(('g_', 's_', 'c_', 'party', 'father', 'addr', 'num', 'paid')):
                del st.session_state[key]
                
        st.rerun()

st.divider()

# --- DASHBOARD: ALL RECORDS & PENDING TRACKER ---
st.subheader("📂 सभी रिकॉर्ड (All Records)")

if not st.session_state.bills:
    st.write("कोई बिल नहीं है। (No bills saved yet.)")
else:
    for b in st.session_state.bills:
        # Determine status and pending days
        is_paid = b['balance'] <= 0
        status_icon = "🟢" if is_paid else "🔴"
        days_pending = (datetime.now().date() - b['date'].date()).days
        
        # Display Card
        with st.expander(f"{status_icon} Bill #{b['bill_no']} | {b['party']} | Date: {b['date'].strftime('%d-%m-%Y')}"):
            st.write(f"**पिता का नाम:** {b['father']} | **पता:** {b['addr']} | **नंबर:** {b['num']}")
            st.markdown("---")
            
            # Show Items
            if b['gold']: 
                st.write("**🥇 सोना (Gold):**")
                for item in b['gold']: st.write(f"- {item['name']} (Rate: {item['rate']}, Wt: {item['wt']}) = ₹{item['price']}")
            if b['silver']: 
                st.write("**🥈 चांदी (Silver):**")
                for item in b['silver']: st.write(f"- {item['name']} (Rate: {item['rate']}, Wt: {item['wt']}) = ₹{item['price']}")
            if b['cloth']: 
                st.write("**👕 कपड़ा (Cloth):**")
                for item in b['cloth']: st.write(f"- {item['name']} = ₹{item['rate']}")
                
            st.markdown("---")
            st.write(f"### कुल बिल (Total): ₹{b['total']:.2f}")
            st.write(f"**अब तक जमा (Total Paid):** ₹{b['paid']:.2f}")
            
            # UPDATE PAYMENT LATER SYSTEM
            if b['balance'] > 0:
                st.error(f"**बकाया (Pending):** ₹{b['balance']:.2f}  ⏳ ({days_pending} दिन हो गए / Days Pending)")
                
                # Add money later interface
                st.write("**बाद में पैसे जमा करें (Add Payment Later):**")
                colA, colB = st.columns([2,1])
                with colA:
                    add_amt = st.number_input("राशि (Amount - ₹)", value=None, format="%.2f", key=f"add_{b['bill_no']}")
                with colB:
                    st.write("") # spacing
                    st.write("")
                    if st.button("जमा करें", key=f"btn_add_{b['bill_no']}"):
                        if add_amt:
                            b['paid'] += add_amt
                            b['balance'] = b['total'] - b['paid']
                            st.rerun()
            else:
                st.success("✅ पूरा भुगतान हो गया (Fully Paid)")
