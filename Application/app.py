import streamlit as st
import streamlit.components.v1 as components
from web3 import Web3
from streamlit_js_eval import streamlit_js_eval
import config
import json

# --- 1. INITIALIZATION & SESSION STATE ---
if 'wallet' not in st.session_state:
    st.session_state.wallet = None

# This tracks which sub-page is currently "active"
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Overview / Dashboard"

# --- WEB3 INITIALIZATION ---
w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
contract = w3.eth.contract(address=w3.to_checksum_address(config.CONTRACT_ADDRESS), abi=config.CONTRACT_ABI)

# --- PAGE SETUP ---
st.set_page_config(page_title=config.APP_NAME, layout="wide")

# --- WALLET INTEGRATION FUNCTION ---
def wallet_integration():
    with st.sidebar:
        st.header("Wallet Connection")
        if st.button("🔌 Link MetaMask Wallet", use_container_width=True):
            address = streamlit_js_eval(
                js_expressions="window.ethereum.request({ method: 'eth_requestAccounts' }).then(accounts => accounts[0])",
                want_output=True,
                key="link_wallet_action"
            )
            if address:
                st.session_state.wallet = address
                st.rerun()

        manual_address = st.text_input("Or paste Wallet Address manually:", placeholder="0x...")
        if manual_address:
            st.session_state.wallet = manual_address

        if st.session_state.wallet:
            st.success(f"Active: {st.session_state.wallet[:6]}...")
            return w3.to_checksum_address(st.session_state.wallet)
        return None

# --- TRANSACTION HELPER ---
def send_transaction(func_name, params, user_address):
    try:
        # 1. Check if the active account in MetaMask matches the intended role
        # 2. Check if the user has enough gas (Sepolia ETH)
        with st.spinner("Preparing Blockchain Transaction..."):
            data = contract.encode_abi(func_name, params)
            tx_dict = {
                "from": user_address,
                "to": config.CONTRACT_ADDRESS,
                "data": data,
                "chainId": hex(config.CHAIN_ID),
                "gas": hex(300000)  # Manual gas limit forces the pop-up to trigger
            }
            
            # This line forces MetaMask to react
            js_code = f"window.ethereum.request({{ method: 'eth_sendTransaction', params: [{json.dumps(tx_dict)}] }})"
            tx_hash = streamlit_js_eval(js_expressions=js_code, want_output=True, key=f"tx_{func_name}_{st.session_state.wallet[-4:]}")
            
            if tx_hash:
                st.success("✅ Transaction Submitted to Sepolia!")
                st.markdown(f"**[View on Etherscan](https://sepolia.etherscan.io/tx/{tx_hash})**")
            else:
                st.warning("⚠️ Action Required: Please open MetaMask and check for a pending request.")
    except Exception as e:
        # This will tell you if the error is "Insufficient Funds" or "User Rejected"
        st.error(f"❌ Blockchain Error: {str(e)}")

# --- UI HEADER ---
def render_header():
    try:
        st.image(config.LOGO_PATH, width=200)
    except:
        st.title(config.APP_NAME)
    st.caption(f"**{config.TAGLINE}**")
    st.divider()

render_header()
active_user = wallet_integration()

# --- ROLE CONFIGURATION ---
ADMIN_WALLET = "0xb0d638A42CE7bdf9201b1420195aA1e2093aa597"
DROPSHIPPER_WALLET = "0xa053d4e3CC2e6C019c429f77C46a5D6Fd316782c"
FORWARDER_WALLET = "0xfdeDbE43e088b85e92c31f6847de0A5f23763b33"
BUYER_WALLET = "0xc52Be894b63FbBAF5BfA8D21C8dc2d4258A4a4bC"

# --- DYNAMIC SIDEBAR LOGIC ---
# The sidebar ONLY shows the current active page or the Home Dashboard
nav_options = ["Overview / Dashboard"]
if st.session_state.active_page != "Overview / Dashboard":
    nav_options.append(st.session_state.active_page)

menu = st.sidebar.radio("Navigation", nav_options)

# --- PORTAL LOGIC (THE LANDING PAGE) ---
if menu == "Overview / Dashboard":
    st.markdown("<h1 style='text-align: center;'>Select Your Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)

    # 1. ADMIN PORTAL
    with col1:
        st.markdown("### 🛡️ Admin")
        if st.button("Access Audit Suite", use_container_width=True):
            if active_user == ADMIN_WALLET:
                st.session_state.active_page = "Admin Audit"
                st.rerun()
            else:
                st.error("Access Denied: Admin wallet required.")

    # 2. DROPSHIPPER PORTAL
    with col2:
        st.markdown("### 📦 Dropshipper")
        if st.button("Access Dispatch Suite", use_container_width=True):
            if active_user == DROPSHIPPER_WALLET:
                st.session_state.active_page = "Create Shipment"
                st.rerun()
            else:
                st.error("Access Denied: Dropshipper wallet required.")

    # 3. FORWARDER PORTAL
    with col3:
        st.markdown("### 🚛 Forwarder")
        if st.button("Access Logistics Hub", use_container_width=True):
            if active_user == FORWARDER_WALLET:
                st.session_state.active_page = "Update Logistics"
                st.rerun()
            else:
                st.error("Access Denied: Forwarder wallet required.")

    # 4. BUYER PORTAL
    with col4:
        st.markdown("### 👤 Buyer")
        if st.button("Access Tracking", use_container_width=True):
            if active_user == BUYER_WALLET:
                st.session_state.active_page = "Customer Feedback"
                st.rerun()
            else:
                st.error("Access Denied: Buyer wallet required.")

    # Footer section from WhatsApp Image 2026-05-05 at 00.06.12.jpeg
    st.divider()
    f1, f2 = st.columns(2)
    with f1:
        st.write("### 🔵 Contact Us")
        st.write(f"Email: {config.CONTACT_EMAIL}")
    with f2:
        st.write("### 🌐 Network Status")
        st.write("System: **Live** | Network: **Sepolia Testnet**")

# --- INDIVIDUAL PORTAL PAGES ---
elif menu == "Admin Audit":
    st.header("Price & Compliance Audit")
    shipment_id = st.text_input("Look up Shipment ID")
    
    if shipment_id:
        shipment_data = contract.functions.shipments(shipment_id).call()
        if shipment_data[6]: # exists
            col1, col2 = st.columns(2)
            with col1:
                total_wei = contract.functions.getTotalPrice(shipment_id).call()
                total_zar = float(total_wei / (10**18 / 60000))
                st.metric("Total Final Cost", f"R{total_zar:.2f}")
            
            with col2:
                is_verified = shipment_data[5] # isVerifiedByAdmin
                st.write(f"Verification Status: {'✅ Verified' if is_verified else '❌ Pending'}")
            
            if not is_verified:
                if st.button("Confirm & Verify Shipment"):
                    send_transaction("adminVerify", [shipment_id], active_user)
        else:
            st.warning("Shipment ID not found in the blockchain records.")

elif menu == "Create Shipment":
    st.header("Register New Shipment")
    with st.form("dropshipper_form"):
        shipment_id = st.text_input("Tracking ID")
        description = st.text_input("Item Description")
        price_zar = st.number_input("Wholesale Price (ZAR)", min_value=0.0)
        if st.form_submit_button("Create Shipment"):
            price_in_wei = int(price_zar * (10**18 / 60000))
            send_transaction("createShipment", [shipment_id, description, price_in_wei], st.session_state.wallet)

elif menu == "Update Logistics":
    st.header("Logistics Operations")
    st.info("The system automatically checks for existing charges to prevent data duplication.")

    # 1. Identification (Outside the form to allow for the 'Check')
    shipment_id = st.text_input("Enter Tracking ID to Load Details", key="log_id")

    if shipment_id:
        try:
            # Call the blockchain to check existing data
            # Based on your ABI: [2] is productPrice, [3] is shippingCharge, [4] is status
            shipment_data = contract.functions.shipments(shipment_id).call()
            
            if not shipment_data[6]:  # shipment_data[6] is 'exists' in your ABI
                st.error("Tracking ID not found in the system.")
            else:
                existing_charge_wei = shipment_data[3]
                # Convert Wei back to ZAR for the UI (1 ETH = 60,000 ZAR)
                existing_charge_zar = float(existing_charge_wei / (10**18 / 60000))
                
                with st.form("logistics_prevention_form"):
                    st.subheader("Update Shipment")
                    
                    # Logic: If price > 0, lock the input to prevent duplication
                    if existing_charge_wei > 0:
                        st.warning(f"💰 Shipping Charge is already set to R{existing_charge_zar:.2f}")
                        price_zar = st.number_input("Shipping Charge (ZAR)", value=existing_charge_zar, disabled=True)
                    else:
                        st.success("No shipping charge recorded yet.")
                        price_zar = st.number_input("Set Shipping Charge (ZAR)", min_value=0.0, step=1.0)
                    
                    status_option = st.selectbox("Update Physical Status", 
                        ["Package Collected", "In Transit", "Out for Delivery", "Delivered"])
                    
                    if st.form_submit_button("Sync to Blockchain"):
                        if st.session_state.wallet:
                            # Convert input to Wei
                            final_price_wei = int(price_zar * (10**18 / 60000))
                            
                            # updateStatus(string _id, string _statusStr, uint256 _charge)
                            params = [shipment_id, status_option, final_price_wei]
                            send_transaction("updateStatus", params, st.session_state.wallet)
                        else:
                            st.error("Please link your wallet in the sidebar.")
        except Exception as e:
            st.error(f"Error loading shipment: {e}")
elif menu == "Customer Feedback":
    st.header("Shipment Details & Feedback")
    
    # 1. SEARCH BOX (The "Trigger" to show details)
    shipment_id = st.text_input("Enter your Tracking ID to view details", key="buyer_search")

    if shipment_id:
        try:
            # Retrieve shipment details from blockchain
            # Mapping based on ABI: [1]=Desc, [2]=ProdPrice, [3]=ShipCharge, [4]=Status, [6]=Exists
            ship_data = contract.functions.shipments(shipment_id).call()

            if not ship_data[6]:
                st.error("Tracking ID not found.")
            else:
                # 2. FINAL PRICE CALCULATION (Product + Shipping)
                # Using your ZAR conversion: 1 ETH = 60,000 ZAR
                total_wei = contract.functions.getTotalPrice(shipment_id).call()
                total_zar = float(total_wei / (10**18 / 60000))
                
                # UI Layout for Shipment Details
                st.subheader(f"Shipment Status: {ship_data[4]}") # Shows Physical Flow
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Item", ship_data[1])
                col2.metric("Total Final Price", f"R{total_zar:.2f}")
                col3.write("**Includes:** Wholesale + Shipping")

                st.divider()

                # 3. FEEDBACK FORM (The Quality Loop)
                st.subheader("Rate Your Experience")
                
                # Check if feedback already exists to prevent duplicate reviews
                existing_review = contract.functions.reviews(shipment_id).call()
                
                if existing_review[2]: # If review.exists is True
                    st.info(f"You previously rated this: {existing_review[0]}/5 Stars")
                    st.write(f"**Your Comment:** {existing_review[1]}")
                else:
                    with st.form("feedback_form"):
                        rating = st.slider("Rating (1-5)", 1, 5, 5)
                        comment = st.text_area("Tell us about the service...")
                        
                        if st.form_submit_button("Submit Final Feedback"):
                            if st.session_state.wallet:
                                # submitFeedback(string _id, uint8 _rating, string _comment)
                                params = [shipment_id, int(rating), comment]
                                send_transaction("submitFeedback", params, st.session_state.wallet)
                            else:
                                st.error("Please link your wallet to submit feedback.")

        except Exception as e:
            st.error(f"Error fetching shipment data: {e}")
