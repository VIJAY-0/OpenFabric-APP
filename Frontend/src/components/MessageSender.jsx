import React, { useState } from 'react';
import axios from 'axios';
import './MessageSender.css'; // Import the CSS
import ModelViewer from './ModelViewer';

const MessageSender = () => {
  const [inputMsg, setInputMsg] = useState('');
  const [session_id, setSession_id] = useState('');
  const [response, setResponse] = useState({ image: '', message: '' , object:''  , session_id:''});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      
      const res = await axios.post('http://localhost:8888/execution', {
          prompt: inputMsg,
          attachments:[],
          session_id:session_id
        });

        console.log(res)
        // const cleaned = res.data.replace(/{'/g, '{"');
        const cleaned = res.data.replace(/\{'/g, '{"')              // {' → {"
                                .replace(/': '/g, '": "')           // ': ' → ": "
                                .replace(/": '/g, '": "')           // ': ' → ": "
                                .replace(/': "/g, '": "')           // ': ' → ": "
                                .replace(/", '/g, '", "')           // ', ' → ", "
                                .replace(/', '/g, '", "')           // ', ' → ", "
                                .replace(/', "/g, '", "')           // ', ' → ", "
                                .replace(/'}/g, '"}')              // '} → "}
                                .replace(/'}/g, '"}')              // '} → "}

        console.log(cleaned)
        
        const parsed = JSON.parse(cleaned);
        setResponse(parsed);
        setSession_id(parsed.session_id);
        console.log(parsed);
        


    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="msg-container">
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

      {error && <div className="msg-error">{error}</div>}

      {(response.message || response.image) && (
        <div className="msg-response">
          <h3>{response.session_id}</h3>
      
          <h2>{response.message}</h2>
          {response.image && (
            <>
             <img
                src={`data:image/png;base64,${response.image}`}
                alt="API response"
                className="msg-image"
              />

              <ModelViewer glbBase64={response.object} imageBase64={response.image} />
              
                </>
              )}
        </div>
      )}
      
    </div>
  );
};

export default MessageSender;





// i want to replace following at once:
// {' -> {"
// '} -> "}
// ': '  -> ": " 
// ', ' -> ", "