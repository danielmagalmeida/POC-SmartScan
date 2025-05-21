import base64
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Configuration
API_URL = "https://api.stag.ssn.visma.ai/v1/transactions"
API_TOKEN = "3m1aKPeUC591TfjNhXch6hTGJIQcL2Pz"
DOCUMENT_PATH = Path("uploads/fruto_ff_M-312_pag8.pdf")
RESULTS_PATH = Path("results")
POLL_INTERVAL_SECONDS = 15

FEATURES = [
    # 📄 Document Information
    "DOCUMENT_TYPE",
    "DOCUMENT_DATE",
    "DOCUMENT_NUMBER",
    "ORDER_NUMBER",
    "PAYMENT_DUE_DATE",
    "CURRENCY",
    "PAYMENT_METHOD",
    "CREDIT_CARD_LAST_FOUR",

    # 🏢 Supplier Details
    "SUPPLIER_NAME",
    "SUPPLIER_ADDRESS",
    "SUPPLIER_COUNTRY_CODE",
    "SUPPLIER_VAT_NUMBER",
    "SUPPLIER_ORGANISATION_NUMBER",

    # 👤 Recipient Details (experimental)
    "RECEIVER_NAME",
    "RECEIVER_ADDRESS",
    "RECEIVER_COUNTRY_CODE",
    "RECEIVER_VAT_NUMBER",
    "RECEIVER_ORDER_NUMBER",

    # 💰 Totals and VAT
    "TOTAL_EXCL_VAT",
    "TOTAL_VAT",
    "TOTAL_INCL_VAT",

    # 🏦 Banking Details
    "IBAN",
    "BIC",
    "BANK_ACCOUNT_NUMBER",
    "BANK_REGISTRATION_NUMBER",

    # 🧾 Line Items
    "PURCHASE_LINES",

    # 🔍 OCR
    # "TEXT_ANNOTATION"
]


def encode_file_to_base64(file_path: Path) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def remove_bounding_boxes(data):
    """
    Recursively remove all 'boundingBox' fields from a JSON object.
    
    Args:
        data: Python dictionary or list (obtained from a JSON)
        
    Returns:
        The same object without 'boundingBox' fields
    """
    if isinstance(data, dict):
        # Create a copy of the dictionary without the 'boundingBox' field
        result = {}
        # Copy all key-value pairs except 'boundingBox'
        for key, value in data.items():
            if key != 'boundingBox':
                result[key] = value
        # Process each value in the dictionary recursively
        for key, value in result.items():
            result[key] = remove_bounding_boxes(value)
        return result
    elif isinstance(data, list):
        # Process each element of the list recursively
        return [remove_bounding_boxes(item) for item in data]
    else:
        # Primitive value (string, number, etc.), return as is
        return data


def enviar_assincrono(remove_bbox=False):
    if not DOCUMENT_PATH.exists():
        print(f"❌ File {DOCUMENT_PATH} not found.")
        return

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    document_base64 = encode_file_to_base64(DOCUMENT_PATH)

    headers = {
        "Authorization": f"Bearer demo",
        "Content-Type": "application/json"
    }

    payload = {
        "document": {
            "content": document_base64
        },
        "features": FEATURES,
        "tags": ["testing"],
        # "customId": f"documento-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    }

    # Send transaction
    print("📤 Sending document for asynchronous processing...")
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Error creating transaction: {response.status_code}")
        print(response.text)
        return

    transaction_id = response.json().get("id")
    if not transaction_id:
        print("❌ Failed to get transactionId.")
        return

    print(f"⏳ Transaction created: {transaction_id}")
    print("🕒 Waiting for completion...")

    # Polling until status changes to DONE
    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        status_response = requests.get(
            f"{API_URL}/{transaction_id}/status", headers=headers)
        status = status_response.json().get("status")
        print(f"🔄 Status: {status}")
        if status == "DONE":
            break
        elif status == "FAILED":
            print("❌ Processing failed.")
            return

    # Get results
    result_response = requests.get(
        f"{API_URL}/{transaction_id}/results", headers=headers)
    if result_response.status_code != 200:
        print("❌ Error retrieving results.")
        print(result_response.text)
        return

    result_json = result_response.json()
    
    # Remove boundingBox if requested
    if remove_bbox:
        print("🔄 Removing 'boundingBox' fields from result...")
        result_json = remove_bounding_boxes(result_json)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_PATH / f"smartscan_async_result_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)

    print(f"✅ Result saved to: {output_file}")
    return result_json


if __name__ == "__main__":
    # Set to True to remove boundingBox fields, False to keep them
    enviar_assincrono(True)
