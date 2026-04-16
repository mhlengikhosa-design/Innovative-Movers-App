# Innovative Movers — Blockchain Event Monitor

A Streamlit app that reads **DisputeRaised** and **DisputeResolved** events
from an Ethereum smart contract on Sepolia testnet, decodes them, and presents
them in a clean read-only dashboard.

---

## Quick Start

### 1. Prerequisites
- Python 3.10 or 3.11 (Python 3.12 also works)
- `pip` and `venv`

### 2. Clone / extract the project
```bash
# If you received a zip:
unzip Application.zip
cd Application
```

### 3. Create a virtual environment
```bash
python -m venv venv

# Activate — Linux / macOS:
source venv/bin/activate

# Activate — Windows PowerShell:
venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. (Optional) configure secrets via .env
```bash
cp .env.example .env
# Edit .env — set your own RPC_URL or CONTRACT_ADDRESS if needed
```
The app works out of the box with the public Sepolia node; `.env` is only
needed if you want to override defaults or use a private RPC key.

### 6. Run the app
```bash
streamlit run app.py
```

The browser will open automatically at **http://localhost:8501**.

---

## Project Structure

```
Application/
├── app.py              ← Main Streamlit application
├── config.py           ← Config + .env loader
├── abi.json            ← Contract ABI
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
├── .gitignore
├── README.md
└── assets/
    └── logo.png        ← (optional) place your logo here
```

---

## Features

| Feature | Description |
|---|---|
| Event Monitor | Browse DisputeRaised / DisputeResolved events with block-frequency chart |
| Shipment Lookup | Search all events by tracking number |
| System Info | Chain ID, latest block, gas price, ABI viewer, status code reference |
| Wallet sidebar | Enter any Ethereum address to see its Sepolia ETH balance |
| CSV export | Download any event query as a CSV file |
| .env support | Override RPC URL and contract address without editing code |

---

## Bugs Fixed (from original)

1. **`@st.cache_data` with Web3 objects** — Web3 connection objects are not
   serialisable. Moved to `@st.cache_resource` with a dedicated factory
   function so the connection is shared safely.

2. **`event_obj().process_log(log)`** — In web3.py v6 the event processor is
   called directly on the class attribute, not on an instantiated object.
   Fixed to `event_obj.process_log(log)`.

3. **`AttributeDict` JSON serialisation** — `event["args"]` returned an
   `AttributeDict` containing `bytes` and `HexBytes`. These are not
   JSON-serialisable, causing silent failures. Added `_safe_serialize()` to
   recursively convert all Web3 types.

4. **Missing `requirements.txt`** — Added with pinned minimum versions.

5. **Hardcoded secrets** — RPC URL and contract address now read from
   environment variables (`.env` supported via `python-dotenv`), with
   sensible defaults so no setup is required for casual use.

6. **Unused status maps** — `SHIPMENT_STATUS` and `PARTICIPANT_STATUS` from
   `config.py` are now rendered in the System Info page and used to label
   `DisputeResolved` events in the Event Monitor.

7. **No error context on decode failures** — Each log now catches exceptions
   individually and records `_decode_error` so one bad log does not kill
   the whole query.
