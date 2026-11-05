import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendChatMessage, sendChatMessageStream } from '../services/api';
import { Send, User, Bot, Sparkles, BookOpen, ChevronRight, Activity, ArrowRight } from 'lucide-react';

export default function Chat({ setActiveCitations, selectedDocumentIds, searchScope, responseLanguage, setResponseLanguage }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const LANGUAGES = ['Auto', 'English', 'Tamil', 'Hindi', 'Spanish', 'French', 'German'];

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textOverride) => {
    const textToSend = typeof textOverride === 'string' ? textOverride : inputValue;
    if (!textToSend.trim()) return;

    const userMessage = { role: 'user', content: textToSend };
    const history = [...messages];
    
    setMessages([...history, userMessage, { role: 'assistant', content: '', citations: [] }]);
    setInputValue("");
    setIsLoading(true);

    try {
      const apiHistory = history.map(m => ({ role: m.role, content: m.content }));
      const docsToSearch = searchScope === 'selected' ? selectedDocumentIds : null;
      
      await sendChatMessageStream(textToSend, apiHistory, docsToSearch, responseLanguage, (chunk) => {
        setMessages(prev => {
          const newMsgs = [...prev];
          const lastMsgIndex = newMsgs.length - 1;
          const lastMsg = { ...newMsgs[lastMsgIndex] };
          
          if (lastMsg.role === 'assistant') {
            if (chunk.type === 'metadata') {
              lastMsg.citations = chunk.citations;
              lastMsg.query_analysis = chunk.query_analysis;
              lastMsg.resources = chunk.resources || [];
            } else if (chunk.type === 'chunk' && chunk.text) {
              lastMsg.content += chunk.text;
            }
          }
          newMsgs[lastMsgIndex] = lastMsg;
          return newMsgs;
        });
      });
    } catch (err) {
      setMessages(prev => {
        const newMsgs = [...prev];
        const lastMsg = newMsgs[newMsgs.length - 1];
        if (lastMsg.role === 'assistant') {
           lastMsg.content += `\n\n**Error:** ${err.message}`;
        }
        return newMsgs;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const showCitations = (citations) => {
    if (citations && citations.length > 0) {
      setActiveCitations(citations);
    }
  };

  const renderRetrievalDetails = (msg) => {
    if (!msg.query_analysis && (!msg.resources || msg.resources.length === 0)) return null;
    return (
      <details className="retrieval-details">
        <summary>
          <Activity size={14} /> How this answer was generated
        </summary>
        <div className="retrieval-content">
          {msg.query_analysis && (
            <div className="retrieval-grid">
              <span>Intent:</span> <span>{msg.query_analysis.intent}</span>
              <span>Complexity:</span> <span>{msg.query_analysis.complexity}</span>
              <span>Confidence:</span> <span>{(msg.query_analysis.confidence * 100).toFixed(1)}%</span>
            </div>
          )}
          {msg.resources && msg.resources.length > 0 && (
            <div style={{marginTop: '10px', paddingTop: '10px', borderTop: '1px dashed var(--border-strong)'}}>
              <strong style={{color: 'var(--text-primary)', display: 'block', marginBottom: '8px'}}>Extracted Resources:</strong>
              <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                {msg.resources.map((res, i) => (
                  <div key={i} style={{backgroundColor: 'var(--bg-primary)', padding: '8px', borderRadius: '4px', fontSize: '0.8rem'}}>
                    <div style={{color: 'var(--accent)', fontWeight: 600, marginBottom: '4px'}}>{res.document_name} (Page {res.page_number})</div>
                    <div style={{fontStyle: 'italic', color: 'var(--text-secondary)'}}>&quot;{res.exact_quote}&quot;</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </details>
    );
  };

  const processContent = (content, citations) => {
    // If no citations, just render the markdown
    if (!citations || citations.length === 0) return content;
    
    // Convert [1], [2] to inline citation pills
    // (This is a simplified replacer, react-markdown handles links/etc normally)
    return content.replace(/\[(\d+)\]/g, (match, p1) => {
      // Return a special placeholder we can target, or just standard markdown link format
      // that we can style in CSS
      return `[${p1}](#citation-${p1})`;
    });
  };

  return (
    <div className="chat-workspace">
      
      {messages.length === 0 ? (
        <div className="chat-empty-state">
          <Sparkles size={48} className="empty-icon" />
          <h2>Document Intelligence Ready</h2>
          <p>Ask a question, extract data, or summarize the key points of your uploaded documents.</p>
          
          <div className="suggested-questions">
            {[
              "What are the key findings in the recent report?",
              "Summarize the main risks mentioned in the documents.",
              "Compare the metrics between the selected documents.",
              "Can you explain the methodology section in simple terms?"
            ].map((q, i) => (
              <button 
                key={i} 
                className="suggested-question-btn"
                onClick={() => handleSend(q)}
                disabled={isLoading}
              >
                <span>{q}</span>
                <ArrowRight size={16} className="arrow" />
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              {msg.role === 'assistant' && (
                <div className="message-avatar assistant">
                  <Bot size={20} />
                </div>
              )}
              
              <div className="message">
                <div className="message-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {processContent(msg.content, msg.citations)}
                  </ReactMarkdown>
                </div>
                
                {msg.role === 'assistant' && msg.content && (
                  <div className="message-actions">
                    {msg.citations && msg.citations.length > 0 && (
                      <button 
                        className="action-pill"
                        onClick={() => showCitations(msg.citations)}
                      >
                        <BookOpen size={14} /> View Sources ({msg.citations.length})
                      </button>
                    )}
                  </div>
                )}
                
                {msg.role === 'assistant' && msg.content && renderRetrievalDetails(msg)}
              </div>

              {msg.role === 'user' && (
                <div className="message-avatar user">
                  <User size={20} />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && messages.length > 0 && messages[messages.length - 1].role !== 'assistant' && (
            <div className="message-wrapper assistant">
              <div className="message-avatar assistant">
                <Bot size={20} />
              </div>
              <div className="message">
                <div className="message-content" style={{color: 'var(--text-muted)'}}>
                  Thinking...
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      )}

      <div className="chat-input-wrapper">
        <div className="language-chips">
          {LANGUAGES.map(lang => (
            <button
              key={lang}
              className={`lang-chip ${responseLanguage === lang ? 'active' : ''}`}
              onClick={() => setResponseLanguage(lang)}
              disabled={isLoading}
              title={`Translate response to ${lang}`}
            >
              {lang === 'Auto' ? '🌐' : ''} {lang}
            </button>
          ))}
        </div>
        <div className="chat-input-container">
          <textarea 
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={searchScope === 'all' ? "Ask anything about your documents..." : "Ask about the selected documents..."}
            disabled={isLoading}
            rows={1}
          />
          <button 
            className="send-btn" 
            onClick={() => handleSend()} 
            disabled={isLoading || !inputValue.trim()}
            title="Send Message"
          >
            <Send size={18} />
          </button>
        </div>
        <div className="input-footer">
          <div className="input-footer-left">
            <span>Scope: {searchScope === 'all' ? 'All documents' : 'Selected documents'}</span>
          </div>
          <span className="hide-mobile">Shift + Enter for new line</span>
        </div>
      </div>
      
    </div>
  );
}
