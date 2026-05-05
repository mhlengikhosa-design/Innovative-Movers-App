# =============================================================================
# CONFIGURATION FILE: Innovative Movers
# =============================================================================
# SECTION 1: SYSTEM IDENTITY - Branding and non-technical descriptions
# SECTION 2: BLOCKCHAIN NETWORK - Connection details for the Sepolia Testnet
# SECTION 3: CONTRACT DETAILS - The address and the "rules" (ABI) of the contract
# SECTION 4: HUMAN READABLE LABELS - Translating code numbers into English
# =============================================================================

# --- SECTION 1: SYSTEM IDENTITY ---
APP_NAME = "Innovative Movers"
TAGLINE = "Immutable Supply Chain Transparency"
SYSTEM_DESCRIPTION = "A blockchain system ensuring honest pricing and tracking for buyers, dropshippers, and forwarders."
CONTACT_EMAIL = "innovativemovers2@gmail.com"
LOGO_PATH = "CompanyLogo.jpeg"
PRIMARY_COLOR = "#007BFF"

# --- SECTION 2: BLOCKCHAIN NETWORK ---
# The public entrance to the Sepolia Ethereum network
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
CHAIN_ID = 11155111  # The specific ID for the Sepolia Testnet

# --- SECTION 3: CONTRACT DETAILS ---
# The digital address where the contract lives on the blockchain
CONTRACT_ADDRESS = "0x62d3500e0804Dc09481bBAc2D1B2E15BCf30828C"

# The Application Binary Interface (ABI) acts as a bridge between Python and Solidity
CONTRACT_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "id", "type": "string"}], "name": "AdminVerified", "type": "event"},
    {"inputs": [{"internalType": "string", "name": "_id", "type": "string"}], "name": "adminVerify", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_id", "type": "string"}, {"internalType": "string", "name": "_desc", "type": "string"}, {"internalType": "uint256", "name": "_price", "type": "uint256"}], "name": "createShipment", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "id", "type": "string"}, {"indexed": False, "internalType": "uint8", "name": "rating", "type": "uint8"}], "name": "FeedbackSubmitted", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "id", "type": "string"}, {"indexed": False, "internalType": "uint256", "name": "price", "type": "uint256"}], "name": "ShipmentCreated", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "id", "type": "string"}, {"indexed": False, "internalType": "uint8", "name": "newStatus", "type": "uint8"}, {"indexed": False, "internalType": "uint256", "name": "charge", "type": "uint256"}], "name": "StatusUpdated", "type": "event"},
    {"inputs": [{"internalType": "string", "name": "_id", "type": "string"}, {"internalType": "uint8", "name": "_rating", "type": "uint8"}, {"internalType": "string", "name": "_comment", "type": "string"}], "name": "submitFeedback", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_id", "type": "string"}, {"internalType": "string", "name": "_statusStr", "type": "string"}, {"internalType": "uint256", "name": "_charge", "type": "uint256"}], "name": "updateStatus", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "admin", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_id", "type": "string"}], "name": "getTotalPrice", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "reviews", "outputs": [{"internalType": "uint8", "name": "rating", "type": "uint8"}, {"internalType": "string", "name": "comment", "type": "string"}, {"internalType": "bool", "name": "exists", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "shipments", "outputs": [{"internalType": "string", "name": "trackingId", "type": "string"}, {"internalType": "string", "name": "description", "type": "string"}, {"internalType": "uint256", "name": "productPrice", "type": "uint256"}, {"internalType": "uint256", "name": "shippingCharge", "type": "uint256"}, {"internalType": "uint8", "name": "status", "type": "uint8"}, {"internalType": "bool", "name": "isVerifiedByAdmin", "type": "bool"}, {"internalType": "bool", "name": "exists", "type": "bool"}, {"internalType": "address", "name": "dropshipper", "type": "address"}, {"internalType": "address", "name": "forwarder", "type": "address"}], "stateMutability": "view", "type": "function"}
]

# --- SECTION 4: HUMAN READABLE LABELS ---
# Maps numeric status codes to English words for the UI
STATUS_MAP = {
    0: "Created",
    1: "Collected",
    2: "In Transit",
    3: "Out For Delivery",
    4: "Delivered"
}
