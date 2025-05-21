# Invoice Data Extraction - Visma ML API Test

This POC demonstrates how to extract invoice data using the Visma ML API. It processes invoice documents asynchronously and stores the results in JSON format.

## Features

- Asynchronous document processing through Visma ML API
- Support for PDF and image-based invoices
- Extraction of multiple invoice data fields
- Optional removal of bounding box coordinates to reduce JSON file size
- Standalone utility for bounding box removal from existing JSON files

## Setup

1. Clone this repository to your local machine
2. Install the Python dependencies:

```
pip install -r requirements.txt
```

3. Place your invoice documents (PDF, PNG, JPG, JPEG, TIFF) in the `uploads/` folder

## Usage

### Asynchronous Processing

Run the main script to process an invoice document:

```
python app.py
```

The script will:
1. Upload the document to the Visma API
2. Poll for processing status
3. Save the results to a timestamped JSON file in the `results/` folder

By default, the script is configured to remove bounding box data from the results. You can change this by modifying the parameter in the main function call: `enviar_assincrono(remove_bbox=True/False)`

## Extracted Fields

The application extracts the following invoice fields:

### Document Information
- Document Type
- Document Date
- Document Number
- Order Number
- Payment Due Date
- Currency
- Payment Method

### Supplier Details
- Supplier Name
- Supplier Address
- Supplier Country Code
- Supplier VAT Number
- Supplier Organization Number

### Recipient Details
- Receiver Name
- Receiver Address
- Receiver Country Code
- Receiver VAT Number
- Receiver Order Number

### Financial Information
- Total Amount (Excluding VAT)
- VAT Amount
- Total Amount (Including VAT)

### Banking Details
- IBAN
- BIC
- Bank Account Number
- Bank Registration Number

### Line Items
- Purchase Lines (product details)

## Technologies Used

- Python 3.x
- Requests library
- FastAPI
- React.js
- Visma ML API

## Web Interface

This project includes a React-based web interface for easier interaction with the Visma SmartScan API.

### Frontend Setup

1. Install Node.js dependencies:
```powershell
cd smartscan-web
npm install
```

2. Start the React development server:
```powershell
cd smartscan-web
npm start
```
The frontend will be available at http://localhost:3000

### Backend Setup

1. Ensure Python virtual environment is activated:
```powershell
.venv\Scripts\activate
```

2. Install backend dependencies:
```powershell
pip install -r visma_invoice_test/requirements.txt
```

3. Start the FastAPI backend:
```powershell
python visma_invoice_test/app.py
```
The API will be available at http://localhost:8000

### Using the Web Interface

1. Open http://localhost:3000 in your browser
2. Use the file upload form to select an invoice document
3. Click "Upload" to process the document
4. The system will display a loading indicator while processing
5. Once complete, you'll receive a confirmation message

You can find the processed results in the `results` folder as JSON files.
