import json
import os
from dotenv import load_dotenv

# Load .env if present (never commit secrets)
load_dotenv()

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- BLOCKCHAIN CONFIG (env vars override defaults) ---
CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    "0x663101bd02258939D30a34EFebefB7b094f0C32E"
)
RPC_URL = os.getenv(
    "RPC_URL",
    "https://ethereum-sepolia-rpc.publicnode.com"
)

# --- LOAD ABI SAFELY ---
_abi_path = os.path.join(BASE_DIR, "abi.json")
if not os.path.exists(_abi_path):
    raise FileNotFoundError(f"abi.json not found at {_abi_path}")

with open(_abi_path, "r") as f:
    CONTRACT_ABI = json.load(f)

# --- BRANDING ---
APP_NAME = "Innovative Movers"
TAGLINE  = "Trustless Logistics, Cryptographic Proof"
DESCRIPTION = (
    "A blockchain-powered traceability system ensuring transparency "
    "and security for international freight."
)
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

# --- STATUS MAPS ---
PARTICIPANT_STATUS = {
    0: "Unregistered",
    1: "Applied (Awaiting Verification)",
    2: "Verified Member",
    3: "Suspended",
}

SHIPMENT_STATUS = {
    0: "Awaiting Pickup",
    1: "In Transit",
    2: "Delivered",
    3: "Disputed",
    4: "Resolved",
    5: "Cancelled",
}
