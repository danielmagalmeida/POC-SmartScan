import base64
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil

# Configuration
API_URL_SYNC = "https://api.stag.ssn.visma.ai/v1/document:annotate"
API_URL_ASYNC = "https://api.stag.ssn.visma.ai/v1/transactions"
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
    "CUSTOMER_NUMBER",

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


def enviar_assincrono(file_path: Path, remove_bbox=False):
    if not file_path.exists():
        print(f"❌ File {file_path} not found.")
        return

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    document_base64 = encode_file_to_base64(file_path)

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "document": {
            "content": document_base64
        },
        "features": convert_features_to_objects(FEATURES),
        "tags": ["moloni-test"],
        # "customId": f"documento-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    }
    
    params = {
        "minConfidence": "VERY_LOW"
    }
    
    try_async_request = True
    
        # Send transaction
    print("📤 Sending document for synchronous processing...")
    # result_response = requests.post(API_URL_SYNC, headers=headers, json=payload)
    # if result_response.status_code == 200:
    #     try_async_request = False
    

    if try_async_request:
        
        payload = {
            "document": {
                "content": document_base64
            },
            "features": FEATURES,
            "tags": ["moloni-test"],
            # "customId": f"documento-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
        # Send transaction
        print("📤 Sending document for asynchronous processing...")
        response = requests.post(API_URL_ASYNC, headers=headers, json=payload)
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
                f"{API_URL_ASYNC}/{transaction_id}/status", headers=headers)
            status = status_response.json().get("status")
            print(f"🔄 Status: {status}")
            if status == "DONE":
                break
            elif status == "FAILED":
                print("❌ Processing failed.")
                return

        # Get results
        result_response = requests.get(
            f"{API_URL_ASYNC}/{transaction_id}/results", headers=headers, params=params)
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
    return result_json  # Este JSON será enviado para o frontend


app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens. Ajuste conforme necessário.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = UPLOAD_FOLDER / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Chama a função enviar_assincrono com o arquivo enviado
    try:
        result = enviar_assincrono(file_path, remove_bbox=True)
        return JSONResponse(content={"message": "File processed successfully", "result": result}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def send_feedback(feedback_data: dict):
    """
    Endpoint para enviar feedback ao Visma Smart Scan API.
    Recebe os campos de feedback do frontend e os envia para o endpoint v1/feedback/create.
    
    Documentação: https://docs.vml.visma.ai/smartscan/api-reference/
    """
    print("🔍 Received feedback data:", feedback_data)
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "id": feedback_data['transactionId'],
            "tags": ["moloni-test"],
            "true_values": feedback_data['fields'],
        }

        response = requests.post(
            "https://api.stag.ssn.visma.ai/v1/feedback:create",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return JSONResponse(content={"message": "Feedback sent successfully", "response": response.json()}, status_code=200)
        else:
            return JSONResponse(
                content={
                    "message": "Failed to send feedback", 
                    "error": response.text, 
                    "status_code": response.status_code
                }, 
                status_code=400
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_features_to_objects(features_list):
    """
    Converte uma lista de strings em uma lista de objetos com formato { "type": feature_name }
    Útil para endpoints que esperam features como objetos.
    
    Args:
        features_list: Lista de strings com nomes das features
        
    Returns:
        Lista de dicionários no formato { "type": feature_name }
    """
    return [{"type": feature} for feature in features_list]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
