import React, { useState, useRef } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const formRef = useRef(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setMessage('');
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResultData(response.data.result);
      setMessage(response.data.message || 'File uploaded successfully!');
    } catch (error) {
      setMessage(error.response?.data?.error || 'An error occurred while uploading the file.');
    } finally {
      setLoading(false);
    }
  };

  // Função para coletar todos os valores dos inputs e enviar como feedback
  const handleSaveFeedback = async () => {
    if (!resultData || !resultData.id) {
      setFeedbackMessage('No document data available to send feedback for.');
      return;
    }

    // Coletar todos os valores dos campos
    const feedbackData = {
      transactionId: resultData.id, // ID da transação original
      fields: {}
    };

    // Coletar valores dos campos normais (ignorando campos vazios)
    document.querySelectorAll('.field-item input').forEach(input => {
      // Apenas incluir campos que não estão vazios
      if (input.value.trim() !== '') {
        const fieldName = input.closest('.field-item').querySelector('.field-label').textContent;
        feedbackData.fields[fieldName] = input.value.trim();
      }
    });

    // Coletar valores da tabela de linhas de compra
    const purchaseLines = [];
    document.querySelectorAll('.purchase-lines-table tbody tr').forEach((row, index) => {
      const lineItem = {};
      let hasValue = false; // Flag para verificar se a linha tem pelo menos um valor não-vazio
      
      row.querySelectorAll('td input').forEach((input, cellIndex) => {
        const headerTitle = document.querySelector(`.purchase-lines-table thead th:nth-child(${cellIndex + 1})`).getAttribute('title');
        if (headerTitle && input.value.trim() !== '') {
          lineItem[headerTitle] = input.value.trim();
          hasValue = true; // A linha tem pelo menos um campo com valor
        }
      });
      
      // Só adicionar a linha se tiver pelo menos um valor não-vazio
      if (hasValue) {
        purchaseLines.push(lineItem);
      }
    });

    if (purchaseLines.length > 0) {
      feedbackData.fields['PURCHASE_LINES'] = purchaseLines;
    }
    
    // Se não houver campos para enviar, mostrar mensagem e não enviar requisição
    if (Object.keys(feedbackData.fields).length === 0) {
      setFeedbackMessage('No fields were modified. Nothing to send.');
      return;
    }

    // Enviar os dados para o backend
    setFeedbackLoading(true);
    setFeedbackMessage('');
    console.log('Sending feedback data:', feedbackData);
    try {
      const response = await axios.post('http://localhost:8000/feedback', feedbackData);
      console.log('Feedback response:', response.data);
      setFeedbackMessage(response.data.message || 'Feedback sent successfully!');
    } catch (error) {
      console.error('Feedback error:', error);
      setFeedbackMessage(
        error.response?.data?.error || 
        `Error: ${error.message}. Status: ${error.response?.status || 'unknown'}`
      );
    } finally {
      setFeedbackLoading(false);
    }
  };

  // Função para renderizar campos por categoria
  const renderFieldsInCategory = (annotations, fieldNames) => {
    if (!annotations) return null;
    
    return fieldNames.map(fieldName => {
      // Encontrar a anotação para esse campo
      const annotation = annotations.find(a => a.feature === fieldName);
      
      // Verificar se a anotação existe
      if (annotation && annotation.candidates && annotation.candidates.length > 0) {
        const candidate = annotation.candidates[0];
        
        // Verificar se o valor existe (pode ser "", 0, false que são valores válidos)
        if (candidate.value !== undefined && candidate.value !== null) {
          return (
            <div key={fieldName} className="field-item">
              <div className="field-label">{fieldName}</div>
              <input 
                type="text" 
                className="field-value" 
                defaultValue={candidate.value} 
              />
              <div className="field-metadata">
                <span className="confidence">
                  Confidence: {candidate.confidence?.level || 'N/A'}
                </span>
              </div>
            </div>
          );
        }
      }
      
      // Campo não encontrado ou sem candidatos válidos, exibir campo vazio
      return (
        <div key={fieldName} className="field-item">
          <div className="field-label">{fieldName}</div>
          <input 
            type="text" 
            className="field-value" 
            defaultValue="" 
          />
          <div className="field-metadata">
            <span className="confidence missing">
              Valor não encontrado
            </span>
          </div>
        </div>
      );
    });
  };

  // Função para renderizar as linhas de compra (PURCHASE_LINES)
  const renderPurchaseLines = (annotations) => {
    if (!annotations) return null;
    
    const purchaseLineAnnotation = annotations.find(a => a.feature === "PURCHASE_LINES");
    if (!purchaseLineAnnotation || !purchaseLineAnnotation.purchaseLineCandidates || 
        purchaseLineAnnotation.purchaseLineCandidates.length === 0) {
      return <p>Nenhuma linha de item encontrada.</p>;
    }
    
    const purchaseLines = purchaseLineAnnotation.purchaseLineCandidates;
    
    return (
      <div className="purchase-lines-container">
        <div className="purchase-lines-table">
          <table>
            <thead>
              <tr>
                <th title="code">Código</th>
                <th title="itemNumber">Número</th>
                <th title="description">Descrição</th>
                <th title="quantity">Quantidade</th>
                <th title="unit">Unidade</th>
                <th title="unitPrice">Preço Unit.</th>
                <th title="unitPriceExclVat">Preço Unit. (Exc. IVA)</th>
                <th title="unitPriceInclVat">Preço Unit. (Inc. IVA)</th>
                <th title="totalAmount/total">Total</th>
                <th title="totalExclVat">Total (Exc. IVA)</th>
                <th title="totalInclVat">Total (Inc. IVA)</th>
                <th title="totalVat">IVA Total</th>
                <th title="percentageVat">% IVA</th>
                <th title="pageRef">Página</th>
              </tr>
            </thead>
            <tbody>
              {purchaseLines.map((line, index) => (
                <tr key={index}>
                  <td><input type="text" defaultValue={line.code || ''} /></td>
                  <td><input type="text" defaultValue={line.itemNumber || ''} /></td>
                  <td><input type="text" defaultValue={line.description || ''} /></td>
                  <td><input type="text" defaultValue={line.quantity || ''} /></td>
                  <td><input type="text" defaultValue={line.unit || ''} /></td>
                  <td><input type="text" defaultValue={line.unitPrice || ''} /></td>
                  <td><input type="text" defaultValue={line.unitPriceExclVat || ''} /></td>
                  <td><input type="text" defaultValue={line.unitPriceInclVat || ''} /></td>
                  <td><input type="text" defaultValue={line.totalAmount || line.total || ''} /></td>
                  <td><input type="text" defaultValue={line.totalExclVat || ''} /></td>
                  <td><input type="text" defaultValue={line.totalInclVat || ''} /></td>
                  <td><input type="text" defaultValue={line.totalVat || ''} /></td>
                  <td><input type="text" defaultValue={line.percentageVat || ''} /></td>
                  <td><input type="text" defaultValue={line.pageRef || ''} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className='file-upload-container'>
      <h1>POC: VML Smartscan</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>Upload</button>
      </form>
      {loading && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      )}
      {message && <p className="message">{message}</p>}
      {feedbackMessage && <p className="feedback-message">{feedbackMessage}</p>}
      
      {resultData && (
        <div className="json-result">
          <h2>Document Analysis Results:</h2>
          {!feedbackLoading && (
            <button 
              className="save-feedback-btn" 
              onClick={handleSaveFeedback}
              disabled={feedbackLoading}
            >
              {feedbackLoading ? 'Sending...' : 'Save Feedback'}
            </button>
          )}
          {feedbackLoading && (
            <div className="spinner-container small">
              <div className="spinner"></div>
              <p>Sending feedback...</p>
            </div>
          )}
          
          {/* Document Information */}
          <div className="category-container">
            <h3 className="category-title">📄 Document Information</h3>
            <div className="fields-container">
              {renderFieldsInCategory(resultData.annotations, [
                "DOCUMENT_TYPE",
                "DOCUMENT_DATE",
                "DOCUMENT_NUMBER",
                "ORDER_NUMBER",
                "PAYMENT_DUE_DATE",
                "CURRENCY",
                "PAYMENT_METHOD",
                "CREDIT_CARD_LAST_FOUR"
              ])}
            </div>
          </div>
          
          {/* Supplier Details */}
          <div className="category-container">
            <h3 className="category-title">🏢 Supplier Details</h3>
            <div className="fields-container">
              {renderFieldsInCategory(resultData.annotations, [
                "SUPPLIER_NAME",
                "SUPPLIER_ADDRESS",
                "SUPPLIER_COUNTRY_CODE",
                "SUPPLIER_VAT_NUMBER",
                "SUPPLIER_ORGANISATION_NUMBER"
              ])}
            </div>
          </div>
          
          {/* Recipient Details */}
          <div className="category-container">
            <h3 className="category-title">👤 Recipient Details</h3>
            <div className="fields-container">
              {renderFieldsInCategory(resultData.annotations, [
                "RECEIVER_NAME",
                "RECEIVER_ADDRESS",
                "RECEIVER_COUNTRY_CODE",
                "RECEIVER_VAT_NUMBER",
                "RECEIVER_ORDER_NUMBER",
                "CUSTOMER_NUMBER"
              ])}
            </div>
          </div>
          
          {/* Totals and VAT */}
          <div className="category-container">
            <h3 className="category-title">💰 Totals and VAT</h3>
            <div className="fields-container">
              {renderFieldsInCategory(resultData.annotations, [
                "TOTAL_EXCL_VAT",
                "TOTAL_VAT",
                "TOTAL_INCL_VAT"
              ])}
            </div>
          </div>
          
          {/* Banking Details */}
          <div className="category-container">
            <h3 className="category-title">🏦 Banking Details</h3>
            <div className="fields-container">
              {renderFieldsInCategory(resultData.annotations, [
                "IBAN",
                "BIC",
                "BANK_ACCOUNT_NUMBER",
                "BANK_REGISTRATION_NUMBER"
              ])}
            </div>
          </div>
          
          {/* Purchase Lines */}
          <div className="category-container">
            <h3 className="category-title">🧾 Line Items</h3>
            {renderPurchaseLines(resultData.annotations)}
          </div>
          
          {/* JSON completo para testes */}
          <div className="full-json-section">
            <details>
              <summary>Mostrar JSON Completo (Para testes)</summary>
              <div className="json-container">
                <pre className="json-code">{JSON.stringify(resultData, null, 2)}</pre>
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
