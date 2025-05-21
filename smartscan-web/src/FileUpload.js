import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

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
      setMessage(response.data.message || 'File uploaded successfully!');
    } catch (error) {
      setMessage(error.response?.data?.error || 'An error occurred while uploading the file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='file-upload-container'>
      <h1>SmartScan POC</h1>
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
      {message && <p>{message}</p>}
    </div>
  );
};

export default FileUpload;
