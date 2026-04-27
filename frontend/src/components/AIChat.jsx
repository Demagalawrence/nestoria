import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Bot, User, Minimize2, Maximize2, X } from 'lucide-react';
import api from '../api/axios';
import './AIChat.css';

const AIChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userRole, setUserRole] = useState('tenant');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Get user role from context or localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUserRole(user.role || 'tenant');
    }
    
    // Add welcome message
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: `Hi! I'm your AI assistant for Uganda rental properties. I can help you find hostels, apartments, and rooms in Kampala and other districts. Try asking me about properties near Makerere University, budget-friendly options in UGX, or specific amenities like generators and WiFi. How can I assist you today?`,
        timestamp: new Date()
      }
    ]);

    // Listen for custom event to open chat
    const handleOpenAIChat = () => setIsOpen(true);
    window.addEventListener('openAIChat', handleOpenAIChat);
    
    return () => {
      window.removeEventListener('openAIChat', handleOpenAIChat);
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call AI agent API
      const response = await api.post('/api/ai/chat/', {
        message: inputMessage,
        user_type: userRole,
        conversation_id: 'chat_' + Date.now()
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: response.data.response || 'I apologize, but I encountered an issue processing your request. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Fallback response
      const fallbackMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: 'I\'m having trouble connecting right now. For immediate assistance with Uganda property rentals, please call us at +256 123 456 789 or email support@renthu.ug.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getAssistantName = () => {
    switch (userRole) {
      case 'student':
        return 'Student Assistant';
      case 'tenant':
        return 'Tenant Assistant';
      case 'owner':
        return 'Property Owner Assistant';
      case 'admin':
        return 'Admin Assistant';
      default:
        return 'AI Assistant';
    }
  };

  if (!isOpen) {
    return (
      <div className="ai-chat-fab" onClick={() => setIsOpen(true)}>
        <MessageCircle size={24} />
        <span className="fab-label">AI Assistant</span>
      </div>
    );
  }

  return (
    <div className={`ai-chat-widget ${isMinimized ? 'minimized' : ''}`}>
      <div className="chat-header">
        <div className="header-left">
          <Bot size={20} />
          <div className="header-info">
            <h3>{getAssistantName()}</h3>
            <span className="status">Online</span>
          </div>
        </div>
        <div className="header-actions">
          <button 
            className="action-btn"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Maximize' : 'Minimize'}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button 
            className="action-btn close-btn"
            onClick={() => setIsOpen(false)}
            title="Close"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          <div className="chat-messages">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-avatar">
                  {message.type === 'bot' ? <Bot size={16} /> : <User size={16} />}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.text}</div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div className="message-avatar">
                  <Bot size={16} />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="chat-input">
            <div className="input-wrapper">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                disabled={isLoading}
                maxLength={500}
              />
              <button 
                type="submit" 
                className="send-btn"
                disabled={!inputMessage.trim() || isLoading}
              >
                <Send size={16} />
              </button>
            </div>
            <div className="input-footer">
              <small>Powered by AI • 500 character limit</small>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default AIChat;
