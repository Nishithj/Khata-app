import streamlit as st
from datetime import datetime
import uuid

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
    /* Secondary/Action Buttons */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #f39c12; color: white; font-size: 18px; padding: 10px; border-radius: 8px; margin-bottom: 10px;
    }
    /* Item Pay Button */
    .pay-btn { background-color: #3498db; color: white; }
    /* Distinguish sections */
    .category-header { background-color: #ecf0f1; padding: 10px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px;}
    .search-box { background-color: #dff9fb; padding: 15px; border-radius: 10px; border: 2px solid #c7ecee; margin-bottom: 20px;}
    .customer-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 6px solid #e74c3c; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .item-card { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #ddd; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM MEMORY SETUP ---
if 'bills' not in st.session_state: st.session_state.bills = []
if 'bill_counter' not in st.session_state: st.session_state.bill_counter = 1
if 'g_cnt' not in st.session_state: st.session_state.g_cnt = 1
if 's_cnt' not in st.session_state: st.session_state.s_cnt = 1

st.header("📖 खाता बही (Ledger)")
st.info("💡 **टिप:** बोलकर लिखने के लिए अपने मोबाइल कीबोर्ड के माइक (🎤) का उपयोग करें।")

# ==========================================
# 1. SEARCH & DASHBOARD SECTION (TOP)
# ==========================================
st.markdown("<div class='search-box'><h3>🔍 ग्राहक खोजें (Search)</h3>", unsafe_allow_html=True)
search_query = st.text_input("नाम लिखें (Type Name)...", key="search_box", placeholder="ग्राहक का नाम...")
st.markdown("</div>", unsafe_allow_html=True)

if search_query:
    st.subheader("खोज परिणाम (Search Results)")
    
    # Group bills by Customer Identity (Name + Father + Address)
    unique_customers = {}
    for b in st.session_state.bills:
        if search_query.lower() in b['party'].lower():
            key = f"{b['party']}_{b['father']}_{b['addr']}"
            if key not in unique_customers:
                unique_customers[key] = {
                    'party': b['party'], 'father': b['father'], 'addr': b['addr'], 'bills': []
                }
            unique_customers[key]['bills'].append(b)
            
    if not unique_customers:
        st.warning("कोई ग्राहक नहीं मिला! (No customer found)")
    else:
        for key, cust in unique_customers.items():
            total_pending = sum(b['balance'] for b in cust['bills'])
            
            # Display Customer Card
            st.markdown(f"""
            <div class='customer-card'>
                <h3 style='margin:0; color:#2c3e50;'>👤 {cust['party']}</h3>
                <p style='margin:5px 0; color:#7f8c8d; font-size:18px;'>
                    <b>पिता:</b> {cust['father']} | <b>पता:</b> {cust['addr']}
                </p>
                <h4 style='margin:0; color:#c0392b;'>कुल बकाया: ₹ {total_pending:.2f}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Inside the customer, show their bills and items
            with st.expander("बकाया आइटम देखें और पैसे जमा करें (View & Pay Pending Items)"):
                for b in cust['bills']:
                    if b['balance'] > 0:
                        st.markdown(f"**📝 Bill #{b['bill_no']} | Date: {b['date'].strftime('%d-%m-%Y')}**")
                        
                        for item in b['items']:
                            if item['balance'] > 0:
                                st.markdown(f"<div class='item-card'>", unsafe_allow_html=True)
                                st.write(f"🔹 **{item['name']}**")
                                st.write(f"कुल कीमत: ₹{item['price']:.2f} | पहले जमा: ₹{item['paid']:.2f}")
                                st.error(f"बकाया (Pending): ₹ {item['balance']:.2f}")
                                
                                # Input to pay for this specific item
                                pay_val = st.number_input(f"पैसे जमा करें (Pay for {item['name']})", key=f"pay_{item['id']}", value=None, format="%.2f")
                                
                                if st.button(f"जमा करें (Save Payment)", key=f"btn_{item['id']}", type="secondary"):
                                    if pay_val and pay_val <= item['balance']:
                                        # Update Item Balance
                                        item['paid'] += pay_val
                                        item['balance'] -= pay_val
                                        # Update Bill Balance
                                        b['paid'] += pay_val
                                        b['balance'] -= pay_val
                                        st.success("पैसे सफलतापूर्वक जमा हो गए! (Amount Saved!)")
                                        st.rerun()
                                    elif pay_val and pay_val > item['balance']:
                                        st.error("गलती: जमा राशि बकाया से ज्यादा है! (Amount exceeds pending!)")
                                        
                                st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("---")
    st.divider()

# ==========================================
# 2. NEW BILL CREATION SECTION
# ==========================================
if not search_query: # Hide new bill section if searching
    current_date = datetime.now()
    st.markdown(f"### 📝 नया बिल बनाएं | बिल नंबर: **{st.session_state.bill_counter}**")
    
    # --- PARTY DETAILS ---
    party = st.text_input("ग्राहक का नाम (Party Name) *", key="party", placeholder="नाम लिखें")
    father = st.text_input("पिता का नाम (Father Name)", key="father", placeholder="(Optional)")
    addr = st.text_input("पता (Address)", key="addr", placeholder="(Optional)")
    num = st.text_input("मोबाइल नंबर (Number)", key="num", placeholder="(Optional)")
    
    total_bill_value = 0.0
    all_items = []
    
    # --- 🥇 GOLD SECTION ---
    st.markdown("<div class='category-header'><h3>🥇 सोने का सामान (Gold)</h3></div>", unsafe_allow_html=True)
    for i in range(st.session_state.g_cnt):
        g_name = st.text_input(f"सामान का नाम (Item Name)", key=f"g_name_{i}", placeholder="जैसे: अंगूठी, चेन")
        g_rate = st.number_input(f"भाव (Rate)", value=None, format="%.2f", key=f"g_rate_{i}")
        g_wt = st.number_input(f"वजन (Weight)", value=None, format="%.2f", key=f"g_wt_{i}")
        g_price = st.number_input(f"कुल कीमत (Price - ₹)", value=None, format="%.2f", key=f"g_price_{i}")
        
        if g_name or g_price:
            all_items.append({
                "id": uuid.uuid4().hex, "type": "Gold", "name": g_name, "rate": g_rate, "wt": g_wt, 
                "price": g_price if g_price else 0.0, "paid": 0.0, "balance": 0.0
            })
            if g_price: total_bill_value += g_price
    
    if st.button("➕ सोना और जोड़ें (Add More Gold)", type="secondary"): 
        st.session_state.g_cnt += 1
        st.rerun()
    
    # --- 🥈 SILVER SECTION ---
    st.markdown("<div class='category-header'><h3>🥈 चांदी का सामान (Silver)</h3></div>", unsafe_allow_html=True)
    for i in range(st.session_state.s_cnt):
        s_name = st.text_input(f"सामान का नाम (Item Name)", key=f"s_name_{i}", placeholder="जैसे: पायल, बिछिया")
        s_rate = st.number_input(f"भाव (Rate)", value=None, format="%.2f", key=f"s_rate_{i}")
        s_wt = st.number_input(f"वजन (Weight)", value=None, format="%.2f", key=f"s_wt_{i}")
        s_price = st.number_input(f"कुल कीमत (Price - ₹)", value=None, format="%.2f", key=f"s_price_{i}")
        
        if s_name or s_price:
            all_items.append({
                "id": uuid.uuid4().hex, "type": "Silver", "name": s_name, "rate": s_rate, "wt": s_wt, 
                "price": s_price if s_price else 0.0, "paid": 0.0, "balance": 0.0
            })
            if s_price: total_bill_value += s_price
    
    if st.button("➕ चांदी और जोड़ें (Add More Silver)", type="secondary"): 
        st.session_state.s_cnt += 1
        st.rerun()
    
    st.markdown("---")
    
    # --- GRAND TOTAL & PAYMENT ---
    st.markdown(f"<h2 style='color: #c0392b; text-align: center;'>कुल बिल (Total Value): ₹ {total_bill_value:.2f}</h2>", unsafe_allow_html=True)
    
    paid = st.number_input("आज की जमा राशि (Amount Paid Today - ₹)", min_value=0.0, value=None, format="%.2f", key="paid")
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
        elif not all_items:
            st.warning("कृपया कम से कम एक सामान दर्ज करें! (Please add at least one item)")
        else:
            # Distribute Paid Amount across items automatically
            rem_paid = paid_amt
            for item in all_items:
                if rem_paid >= item['price']:
                    item['paid'] = item['price']
                    item['balance'] = 0.0
                    rem_paid -= item['price']
                else:
                    item['paid'] = rem_paid
                    item['balance'] = item['price'] - rem_paid
                    rem_paid = 0.0 # All money distributed
                    
            new_bill = {
                "bill_no": st.session_state.bill_counter,
                "date": current_date,
                "party": party,
                "father": father if father else "",
                "addr": addr if addr else "",
                "num": num if num else "",
                "items": all_items,
                "total": total_bill_value,
                "paid": paid_amt,
                "balance": balance
            }
            
            # Add to records and increment counter
            st.session_state.bills.insert(0, new_bill)
            st.session_state.bill_counter += 1
            
            # Reset counters
            st.session_state.g_cnt = 1
            st.session_state.s_cnt = 1
            
            # Clear all input boxes
            for key in list(st.session_state.keys()):
                if key.startswith(('g_', 's_', 'party', 'father', 'addr', 'num', 'paid')):
                    del st.session_state[key]
                    
            st.rerun()
