import React, { useState } from 'react';
import axios from 'axios';
import './MessageSender.css';
import ModelViewer from './ModelViewer';
import Loader from './Loader';

const MessageSender = () => {
  const [inputMsg, setInputMsg] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [response, setResponse] = useState({ image: '', message: '', object: '', session_id: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const cleanJSON = (raw) => {
    try {
      return JSON.parse(
        raw
          .replace(/\{'/g, '{"')
          .replace(/': '/g, '": "')
          .replace(/": '/g, '": "')
          .replace(/': "/g, '": "')
          .replace(/", '/g, '", "')
          .replace(/', '/g, '", "')
          .replace(/', "/g, '", "')
          .replace(/'}/g, '"}')
      );
    } catch (err) {
      console.error("Failed to parse response:", err);
      throw new Error('Invalid server response format');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('http://localhost:8888/execution', {
        prompt: inputMsg,
        attachments: [],
        session_id: sessionId
      });

      const parsed = cleanJSON(res.data);
      setResponse(parsed);
      setSessionId(parsed.session_id);
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <>
    <div className="msg-container">
      <div className="heading">
      <h1>Image and 3D Render Generator</h1>
      </div>

      <form className="msg-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputMsg}
          onChange={(e) => setInputMsg(e.target.value)}
          placeholder="Type your message..."
          className="msg-input"
          required
          />
        <button type="submit" className="msg-button" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>


      {loading && <div className="msg-loading">{<Loader/>}</div>}
      {error && <div className="msg-error">{error}</div>}


      {(response.message || response.image) && (
        <div className="msg-response">

          <h2 className="msg-session-id">{response.session_id}</h2>

          <h2 className="msg-message">{response.message}</h2>

          <div className="msg-display-row">

            <div className="msg-display-row-cont">
                      {response.image && (
                        <img
                        src={`data:image/png;base64,${response.image}`}
                        alt="Generated"
                        className="msg-image"
                        />
                      )}
            </div>
            <div className="msg-display-row-cont">
                    {response.object && (
                      <ModelViewer glbBase64={response.object} />
                    )}
            </div>

            
          </div>
        </div>
      )}

    </div>
      </>
  );
};

export default MessageSender;
