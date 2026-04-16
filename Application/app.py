import streamlit as st
from web3 import Web3
import config
import os
import json
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title=config.APP_NAME,
    layout="wide",
    page_icon="🚢",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
st.session_state.setdefault("user_address", None)
st.session_state.setdefault("wallet_ready", False)

# --------------------------------------------------
# WEB3 INIT  (FIX: cache the connection object properly)
# --------------------------------------------------
@st.cache_resource
def get_web3_connection():
    """Cached Web3 connection — avoids reconnecting on every rerun."""
    try:
        w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        if w3.is_connected():
            return w3, True
        return None, False
    except Exception:
        return None, False

w3, rpc_ok = get_web3_connection()

contract_address = Web3.to_checksum_address(config.CONTRACT_ADDRESS)

contract = None
if rpc_ok and w3:
    contract = w3.eth.contract(address=contract_address, abi=config.CONTRACT_ABI)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists(config.LOGO_PATH):
        st.image(config.LOGO_PATH, width=180)
    else:
        st.markdown("# 🚢")

with col_title:
    st.title(config.APP_NAME)
    st.caption(config.TAGLINE)
    st.write(config.DESCRIPTION)

if not rpc_ok:
    st.error("❌ RPC connection failed — check RPC_URL in config.py or your .env file")
else:
    st.success("✅ Connected to Sepolia Testnet")

st.info("📡 Read-only Blockchain Event Explorer")

# --------------------------------------------------
# SIDEBAR — NAVIGATION
# --------------------------------------------------
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Menu", ["Event Monitor", "Shipment Lookup", "System Info"])

# --------------------------------------------------
# SIDEBAR — WALLET
# --------------------------------------------------
st.sidebar.header("🔑 Wallet")
wallet_input = st.sidebar.text_input("Enter wallet address (0x…)")

if wallet_input:
    try:
        checksummed = Web3.to_checksum_address(wallet_input.strip())
        st.session_state.user_address = checksummed
        st.session_state.wallet_ready = True
        st.sidebar.success("✅ Wallet set")
    except Exception:
        st.sidebar.error("❌ Invalid Ethereum address")
        st.session_state.wallet_ready = False

if st.session_state.wallet_ready:
    addr = st.session_state.user_address
    st.sidebar.info(f"`{addr[:6]}…{addr[-4:]}`")
    if rpc_ok and w3:
        try:
            balance_wei = w3.eth.get_balance(addr)
            balance_eth = w3.from_wei(balance_wei, "ether")
            st.sidebar.metric("Balance (ETH)", f"{float(balance_eth):.4f}")
        except Exception:
            pass
else:
    st.sidebar.warning("⚠️ No wallet connected")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def _safe_serialize(obj):
    """Recursively convert Web3/AttributeDict types to JSON-safe Python types."""
    if isinstance(obj, bytes):
        return "0x" + obj.hex()
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(i) for i in obj]
    if hasattr(obj, "items"):          # catches AttributeDict
        return {k: _safe_serialize(v) for k, v in obj.items()}
    return obj


def get_event_signature(w3_instance, event_name, event_abi):
    """Compute keccak256 topic0 for an event."""
    types = ",".join([inp["type"] for inp in event_abi["inputs"]])
    sig = f"{event_name}({types})"
    return "0x" + w3_instance.keccak(text=sig).hex()


# --------------------------------------------------
# EVENT LOADER
# FIX 1: no Web3 objects in cache args (passes address string instead)
# FIX 2: event_obj.process_log(log) — not event_obj().process_log(log)
# FIX 3: _safe_serialize args before storing
# --------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def load_events(event_name: str, block_range: int, _contract_address: str):
    if not rpc_ok or contract is None or w3 is None:
        return []

    latest_block = w3.eth.block_number
    from_block = max(latest_block - block_range, 0)

    event_abi = next(
        (item for item in config.CONTRACT_ABI
         if item.get("type") == "event" and item.get("name") == event_name),
        None,
    )
    if not event_abi:
        return []

    topic0 = get_event_signature(w3, event_name, event_abi)

    logs = w3.eth.get_logs({
        "fromBlock": from_block,
        "toBlock": "latest",
        "address": _contract_address,
        "topics": [topic0],
    })

    event_obj = getattr(contract.events, event_name)   # FIX: class, not instance
    decoded = []
    for log in logs:
        try:
            processed = event_obj.process_log(log)     # FIX: correct web3 v6 call
            decoded.append({
                "event": processed["event"],
                "blockNumber": processed["blockNumber"],
                "transactionHash": processed["transactionHash"].hex(),
                "logIndex": processed["logIndex"],
                "args": _safe_serialize(dict(processed["args"])),  # FIX: safe cast
            })
        except Exception as e:
            decoded.append({
                "event": event_name,
                "blockNumber": log.get("blockNumber"),
                "transactionHash": log["transactionHash"].hex() if "transactionHash" in log else "?",
                "logIndex": log.get("logIndex"),
                "args": {"_decode_error": str(e)},
            })
    return decoded


# ==================================================
# PAGE: SYSTEM INFO
# ==================================================
if menu == "System Info":
    st.header("⚙️ System Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RPC Status", "✅ Connected" if rpc_ok else "❌ Disconnected")
        st.write(f"**RPC URL:** `{config.RPC_URL}`")
    with col2:
        if rpc_ok and w3:
            try:
                st.metric("Chain ID", w3.eth.chain_id)
                st.metric("Latest Block", f"{w3.eth.block_number:,}")
            except Exception as e:
                st.warning(f"Could not fetch chain info: {e}")
    with col3:
        st.write(f"**Contract:** `{contract_address}`")
        st.write("**Network:** Sepolia Testnet")
        if rpc_ok and w3:
            try:
                gwei = w3.from_wei(w3.eth.gas_price, "gwei")
                st.metric("Gas Price (Gwei)", f"{float(gwei):.2f}")
            except Exception:
                pass

    st.divider()
    st.subheader("📋 ABI Events")
    for ev in [e for e in config.CONTRACT_ABI if e.get("type") == "event"]:
        with st.expander(f"Event: **{ev['name']}**"):
            st.json(ev)

    st.subheader("📦 Status Code Reference")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Participant Status**")
        st.table(pd.DataFrame(list(config.PARTICIPANT_STATUS.items()), columns=["Code", "Label"]))
    with col_b:
        st.write("**Shipment Status**")
        st.table(pd.DataFrame(list(config.SHIPMENT_STATUS.items()), columns=["Code", "Label"]))


# ==================================================
# PAGE: SHIPMENT LOOKUP  (new feature)
# ==================================================
elif menu == "Shipment Lookup":
    st.header("🔍 Shipment Lookup")
    st.write("Search all on-chain events for a specific tracking number.")

    tracking_input = st.text_input("Tracking Number", placeholder="e.g. SHIP-001")
    block_range_lookup = st.slider("Block Range to Search", 100, 50000, 10000, step=500)

    if st.button("🔎 Search", disabled=not rpc_ok):
        if not tracking_input.strip():
            st.warning("Please enter a tracking number.")
        else:
            results = []
            with st.spinner("Searching blockchain events…"):
                for ev_name in ["DisputeRaised", "DisputeResolved"]:
                    for e in load_events(ev_name, block_range_lookup, contract_address):
                        if tracking_input.strip().lower() in str(e.get("args", "")).lower():
                            results.append(e)

            if not results:
                st.info(f"No events found for **{tracking_input}** in the last {block_range_lookup:,} blocks.")
            else:
                st.success(f"Found **{len(results)}** event(s) for `{tracking_input}`")
                for i, ev in enumerate(results, 1):
                    with st.expander(f"#{i} — {ev['event']} @ block {ev['blockNumber']}"):
                        st.json(ev)

                st.subheader("📅 Event Timeline")
                df = pd.DataFrame(results)[["blockNumber", "event", "transactionHash"]]
                df = df.sort_values("blockNumber").reset_index(drop=True)
                df.columns = ["Block", "Event", "Tx Hash"]
                st.dataframe(df, use_container_width=True)


# ==================================================
# PAGE: EVENT MONITOR
# ==================================================
elif menu == "Event Monitor":
    st.header("📡 Blockchain Event Monitor")

    col_sel, col_range = st.columns([2, 3])
    with col_sel:
        event_type = st.selectbox("Select Event", ["DisputeRaised", "DisputeResolved"])
    with col_range:
        block_range = st.slider("Block Range", 100, 50000, 5000, step=100)

    if st.button("🔄 Load Events", disabled=not rpc_ok):
        with st.spinner(f"Fetching {event_type} events…"):
            logs = load_events(event_type, block_range, contract_address)

        if not logs:
            st.info("No events found in selected block range.")
        else:
            st.success(f"Found **{len(logs)}** event(s)")

            # Export as CSV
            df = pd.DataFrame(logs)
            st.download_button(
                "⬇️ Download CSV",
                data=df.to_csv(index=False).encode(),
                file_name=f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

            # Summary metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Events", len(logs))
            m2.metric("Earliest Block", f"{min(e['blockNumber'] for e in logs):,}")
            m3.metric("Latest Block", f"{max(e['blockNumber'] for e in logs):,}")

            # Frequency chart
            st.subheader("📊 Events per Block Bucket (100-block intervals)")
            df_chart = df.copy()
            df_chart["blockBucket"] = (df_chart["blockNumber"] // 100) * 100
            chart_data = df_chart.groupby("blockBucket").size().reset_index(name="count")
            st.bar_chart(chart_data.set_index("blockBucket")["count"])

            # Event cards
            st.subheader("📋 Event Details")
            for i, event in enumerate(reversed(logs), start=1):
                label = f"#{i} — Block {event['blockNumber']} | Tx: {event['transactionHash'][:14]}…"
                with st.expander(label):
                    args = event.get("args", {})
                    if event_type == "DisputeResolved" and "finalStatus" in args:
                        status_label = config.SHIPMENT_STATUS.get(
                            args["finalStatus"], f"Unknown ({args['finalStatus']})"
                        )
                        st.success(f"Final Status: {status_label}")
                    st.json(event)
