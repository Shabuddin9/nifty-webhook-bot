from flask import Flask, request, jsonify
from smartapi import SmartConnect
import datetime
import os

app = Flask(__name__)

# ====== CONFIG - Use environment variables ======
API_KEY = os.getenv("SMARTAPI_KEY")
CLIENT_ID = os.getenv("SMARTAPI_CLIENT")
PASSWORD = os.getenv("SMARTAPI_PASS")
TOTP = os.getenv("SMARTAPI_TOTP")
LOT_SIZE = 75 * 5

# ====== Login to Angel SmartAPI ======
obj = SmartConnect(api_key=API_KEY)
session = obj.generateSession(CLIENT_ID, PASSWORD, TOTP)
auth_token = session['data']['jwtToken']

print("✅ SmartAPI Connected")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📩 Received Alert:", data)

    action = data.get("action")

    if action == "BUY_CALL":
        place_order("CE", "BUY")
    elif action == "BUY_PUT":
        place_order("PE", "BUY")
    else:
        print("⚠️ Unknown action:", action)

    return jsonify({"status": "received"}), 200

def place_order(option_type, txn_type):
    expiry = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%d%b%y').upper()
    strike = "25000"  # TODO: Make dynamic later
    symbol = f"NIFTY{expiry}{strike}{option_type}"

    order = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": "XYZ",  # Replace with correct token
        "transactiontype": txn_type,
        "exchange": "NFO",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": LOT_SIZE
    }

    try:
        response = obj.placeOrder(order)
        print("✅ Order Placed:", response)
    except Exception as e:
        print("❌ Order Failed:", str(e))

# ====== Run Server ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
