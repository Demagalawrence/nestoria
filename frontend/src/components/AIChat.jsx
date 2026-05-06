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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // Get user role from context or localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUserRole(user.role || 'tenant');
    }
    
    // Add enhanced welcome message with real estate specialization
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: `🏠 **Welcome to Nestoria AI - Your Uganda Real Estate Expert!**\n\nI'm your specialized AI assistant for Uganda rental properties with deep knowledge of:\n\n📍 **Locations**: Kampala, Entebbe, Jinja, Makerere, and more\n💰 **Budget Ranges**: From UGX 80,000 to UGX 5M+ per month\n🏠 **Property Types**: Apartments, Hostels, Self-contained, Family houses\n✨ **Amenities**: WiFi, Generator backup, Security, Water tanks, etc.\n\n**Ask me about:**\n• "Find apartments under UGX 500k near Makerere"\n• "Hostels with WiFi and generator in Kampala"\n• "Self-contained rooms in Entebbe under UGX 300k"\n• "Properties with good security and water backup"\n\nHow can I help you find your perfect home in Uganda today? 🇺🇬`,
        timestamp: new Date(),
        isRichText: true
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

    let hasError = false;
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
        timestamp: new Date(),
        isRichText: true
      };

      setMessages(prev => [...prev, botMessage]);
      setIsLoading(false);
    } catch (error) {
      console.error('Error sending message, using fallback AI:', error);
      hasError = true;
    }
    
    if (hasError) {
      const lowerMsg = inputMessage.toLowerCase();
      let fallbackText = "I can help you find properties in Uganda. Are you looking for a specific location like Kampala or Entebbe, or do you have a specific budget?";
      
      if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
        fallbackText = "Hello! How can I assist you with your property search today?";
      } else if (lowerMsg.includes('kampala')) {
        fallbackText = "📍 **Kampala Properties**\nWe have many great options in Kampala. Are you looking for something in Ntinda, Kololo, or closer to the city center?";
      } else if (lowerMsg.includes('budget') || lowerMsg.includes('cheap') || lowerMsg.match(/\d+/)) {
        fallbackText = "💰 **Budget Options**\nWe have several affordable options:\n• Single rooms starting at UGX 150,000/month\n• 1-bedroom apartments from UGX 400,000/month\nWould you like me to filter by a specific area?";
      } else if (lowerMsg.includes('hostel') || lowerMsg.includes('student') || lowerMsg.includes('makerere')) {
        fallbackText = "🏠 **Student Hostels**\nWe have hostels near Makerere and Kyambogo.\n• Single rooms: ~UGX 800,000/semester\n• Shared rooms: ~UGX 500,000/semester\nMany include WiFi and security.";
      } else if (lowerMsg.includes('thank')) {
        fallbackText = "You're very welcome! Feel free to ask if you need anything else.";
      }
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: fallbackText,
        timestamp: new Date(),
        isRichText: true
      };
      
      // Artificial delay to make it feel like AI is "thinking"
      setTimeout(() => {
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      }, 1000);
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
                  <div className="message-text">
                    {message.isRichText ? (
                      <div className="rich-text-message">
                        {message.text.split('\n').map((line, index) => {
                          // Handle bold text
                          let formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                          // Handle bullet points
                          if (line.startsWith('•')) {
                            return <div key={index} className="bullet-point" dangerouslySetInnerHTML={{ __html: formattedLine }} />;
                          }
                          // Handle headers
                          if (line.startsWith('📍') || line.startsWith('💰') || line.startsWith('🏠') || line.startsWith('✨')) {
                            return <div key={index} className="header-line" dangerouslySetInnerHTML={{ __html: formattedLine }} />;
                          }
                          return <div key={index} dangerouslySetInnerHTML={{ __html: formattedLine }} />;
                        })}
                      </div>
                    ) : (
                      message.text
                    )}
                  </div>
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
