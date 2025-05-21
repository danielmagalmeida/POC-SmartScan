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
- Visma ML API
