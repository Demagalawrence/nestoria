import React, { useEffect, useState, useRef, useContext } from 'react';
import { MessageCircle, Mail, Phone, HelpCircle, Send, X, Minimize2, Maximize2 } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import './Support.css';

const Support = () => {
  const { user } = useContext(AuthContext);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! Welcome to Nestoria Support. How can I help you today?',
      sender: 'support',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleStartChat = () => {
    setIsChatOpen(true);
    setIsMinimized(false);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
  };

  const handleMinimizeChat = () => {
    setIsMinimized(!isMinimized);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (message.trim() === '') return;

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsTyping(true);

    // Simulate support response
    setTimeout(() => {
      const supportResponses = [
        'Thank you for your message. Let me help you with that.',
        'I understand your concern. Let me check that for you.',
        'That\'s a great question! Here\'s what I can tell you...',
        'I\'m here to help. Could you provide more details about your issue?',
        'Thanks for reaching out! Our team is looking into this for you.'
      ];

      const supportMessage = {
        id: Date.now() + 1,
        text: supportResponses[Math.floor(Math.random() * supportResponses.length)],
        sender: 'support',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, supportMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="support-page">
      {/* Premium Dark Gradient Header */}
      <div className="inner-page-hero">
        <div className="container hero-content-wrapper">
          <h1 className="inner-hero-title">How can we help?</h1>
          <p className="inner-hero-subtitle">Our support team is available 24/7 to assist you with any questions or issues.</p>
        </div>
      </div>
      
      <div className="container support-main-container">
        <div className="support-content">
          <div className="support-options">
            <div className="support-card">
              <div className="support-icon-wrapper chat-icon">
                <MessageCircle size={28} />
              </div>
              <h3>Live Chat</h3>
              <p>Get instant help from our support team via live chat.</p>
              <a href="https://wa.me/25677564321" target="_blank" rel="noopener noreferrer" className="support-action-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>Start Chat</a>
            </div>
            
            <div className="support-card">
              <div className="support-icon-wrapper email-icon">
                <Mail size={28} />
              </div>
              <h3>Email Support</h3>
              <p>Send us a detailed message and we'll respond within 24 hours.</p>
              <a href="mailto:support@renthu.com" className="support-action-btn">Send Email</a>
            </div>
            
            <div className="support-card">
              <div className="support-icon-wrapper phone-icon">
                <Phone size={28} />
              </div>
              <h3>Phone Support</h3>
              <p>Call us for immediate assistance with urgent matters.</p>
              <a href="tel:+15551234567" className="support-action-btn outline-btn">Call Now</a>
            </div>
          </div>
          
          <div className="support-bottom-grid">
            <div className="support-faq">
              <div className="faq-header">
                <h2>Frequently Asked Questions</h2>
                <p>Quick answers to common questions.</p>
              </div>
              <div className="faq-list">
                <div className="faq-item">
                  <h3>How do I reserve a property?</h3>
                  <p>Browse our listings, select your preferred property, choose your dates, and complete the reservation process with secure payment.</p>
                </div>
                <div className="faq-item">
                  <h3>What payment methods do you accept?</h3>
                  <p>We accept all major credit cards, debit cards, and secure online payment methods through our protected payment system.</p>
                </div>
                <div className="faq-item">
                  <h3>Can I cancel my reservation?</h3>
                  <p>Yes, you can cancel your reservation according to our cancellation policy. Check the specific terms for your property.</p>
                </div>
                <div className="faq-item">
                  <h3>How do I list my property?</h3>
                  <p>Create an account as a property owner, complete the verification process, and start listing your properties with detailed information.</p>
                </div>
              </div>
            </div>
            
            <div className="support-sidebar">
              <div className="hours-card">
                <div className="hours-icon"><HelpCircle size={24} /></div>
                <h3>Support Hours</h3>
                <div className="hours-grid">
                  <div className="hours-item">
                    <strong>Monday - Friday:</strong>
                    <span>24/7 Live Support</span>
                  </div>
                  <div className="hours-item">
                    <strong>Saturday:</strong>
                    <span>9:00 AM - 8:00 PM EST</span>
                  </div>
                  <div className="hours-item">
                    <strong>Sunday:</strong>
                    <span>10:00 AM - 6:00 PM EST</span>
                  </div>
                  <div className="hours-item highlight-item">
                    <strong>Emergency:</strong>
                    <span>24/7 Available</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </div>

      {/* Live Chat Modal */}
      {isChatOpen && (
        <div className="chat-modal-overlay">
          <div className={`chat-container ${isMinimized ? 'minimized' : ''}`}>
            {/* Chat Header */}
            <div className="chat-header">
              <div className="chat-header-info">
                <div className="chat-avatar">
                  <MessageCircle size={20} />
                </div>
                <div className="chat-status">
                  <h4>Nestoria Support</h4>
                  <span className="status-indicator online">Online</span>
                </div>
              </div>
              <div className="chat-header-actions">
                <button 
                  className="chat-action-btn"
                  onClick={handleMinimizeChat}
                  title={isMinimized ? "Maximize" : "Minimize"}
                >
                  {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
                </button>
                <button 
                  className="chat-action-btn close-btn"
                  onClick={handleCloseChat}
                  title="Close chat"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Chat Messages */}
            {!isMinimized && (
              <>
                <div className="chat-messages">
                  {messages.map((msg) => (
                    <div 
                      key={msg.id} 
                      className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'support-message'}`}
                    >
                      <div className="message-content">
                        <p>{msg.text}</p>
                        <span className="message-time">{msg.timestamp}</span>
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="chat-message support-message">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Chat Input */}
                <form onSubmit={handleSendMessage} className="chat-input-container">
                  <div className="chat-input-wrapper">
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type your message..."
                      className="chat-input"
                      disabled={isTyping}
                    />
                    <button 
                      type="submit" 
                      className="chat-send-btn"
                      disabled={isTyping || message.trim() === ''}
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Support;
