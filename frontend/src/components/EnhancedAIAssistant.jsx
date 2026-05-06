/**
 * Enhanced AI Assistant with Hostel Reservation Tools
 * Uganda-specific AI assistant to help students reserve hostels
 */

import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, MapPin, DollarSign, CreditCard, Book } from 'lucide-react';
import aiTools from '../utils/aiTools';

const EnhancedAIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initial greeting and suggestions
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const initialMessage = {
        id: Date.now(),
        type: 'assistant',
        content: "🇺🇬 Welcome to RentHu Uganda AI Assistant! I'm here to help you find and reserve the perfect hostel. I can help you with:\n\n🏠 Search for hostels by location, price, or university\n💰 Calculate reservation costs and payment options\n📚 Get information about universities and areas\n🔍 Compare different hostels\n📋 Check reservation status\n💡 Give you helpful tips for reserving in Uganda\n\nHow can I help you today?",
        timestamp: new Date()
      };
      setMessages([initialMessage]);
      
      setSuggestions([
        "Find hostels near Makerere University",
        "Show me hostels under UGX 150,000",
        "Compare hostels in Kikoni and Wandegeya",
        "Help me reserve a room for next semester",
        "What are the best areas for students?",
        "How do I pay with mobile money?",
        "Check my reservation status"
      ]);
    }
  }, [isOpen, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const processUserMessage = async (userInput) => {
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: userInput,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Process the user input and determine which tool to use
      const response = await processAIRequest(userInput);
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.content,
        data: response.data,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update suggestions based on context
      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "Sorry, I encountered an error. Please try again or contact support.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const processAIRequest = async (input) => {
    const lowerInput = input.toLowerCase();
    
    // Check for search intent
    if (lowerInput.includes('search') || lowerInput.includes('find') || lowerInput.includes('looking for')) {
      return await handleSearchRequest(input);
    }
    
    // Check for university info
    if (lowerInput.includes('university') || lowerInput.includes('makerere') || lowerInput.includes('kyambogo')) {
      return await handleUniversityRequest(input);
    }
    
    // Check for area info
    if (lowerInput.includes('area') || lowerInput.includes('kikoni') || lowerInput.includes('wandegeya')) {
      return await handleAreaRequest(input);
    }
    
    // Check for reservation
    if (lowerInput.includes('book') || lowerInput.includes('reserve') || lowerInput.includes('booking')) {
      return await handleReservationRequest(input);
    }
    
    // Check for payment
    if (lowerInput.includes('pay') || lowerInput.includes('payment') || lowerInput.includes('mobile money')) {
      return await handlePaymentRequest(input);
    }
    
    // Check for tips
    if (lowerInput.includes('tips') || lowerInput.includes('advice') || lowerInput.includes('help')) {
      return await handleTipsRequest(input);
    }
    
    // Default response
    return {
      content: "I can help you with hostel reservation in Uganda! Try asking me to:\n\n🏠 Search for hostels in a specific area\n📚 Get information about universities\n💰 Check prices and payment options\n📋 Help with reserving a room\n🔍 Compare different hostels\n\nWhat would you like to know?",
      suggestions: [
        "Find hostels near Makerere University",
        "Show me hostels under UGX 150,000",
        "How do I pay with mobile money?",
        "What are the best areas for students?"
      ]
    };
  };

  const handleSearchRequest = async (input) => {
    // Extract search parameters from input
    const location = extractLocation(input);
    const maxPrice = extractPrice(input);
    const university = extractUniversity(input);
    
    const searchTool = aiTools.find(tool => tool.name === 'search_hostels');
    const result = await searchTool.execute({
      location,
      max_price: maxPrice,
      university
    });
    
    if (result.success) {
      const hostelList = result.hostels.map(hostel => 
        `🏠 **${hostel.name}**\n📍 ${hostel.location}\n💰 UGX ${hostel.price.toLocaleString()}/month\n⭐ ${hostel.rating}/5\n${hostel.description.substring(0, 100)}...\n`
      ).join('\n\n');
      
      return {
        content: `I found ${result.count} hostels matching your criteria:\n\n${hostelList}\n\nWould you like more details about any of these hostels, or would you like me to help you reserve one?`,
        data: result.hostels,
        suggestions: [
          "Show me more details about the first hostel",
          "Help me reserve the second hostel",
          "Compare these hostels",
          "Search with different criteria"
        ]
      };
    } else {
      return {
        content: result.message,
        suggestions: ["Try a different location", "Increase your budget", "Search by university"]
      };
    }
  };

  const handleUniversityRequest = async (input) => {
    const university = extractUniversity(input);
    const uniTool = aiTools.find(tool => tool.name === 'get_university_info');
    const result = await uniTool.execute({ university });
    
    if (result.success) {
      const uni = result.university;
      return {
        content: `📚 **${uni.name}**\n\n📍 Location: ${uni.location}\n👥 Students: ${uni.student_population.toLocaleString()}\n💰 Average hostel price: UGX ${uni.average_price.toLocaleString()}/month\n🏠 Nearby hostels: ${uni.nearby_hostels_count}\n\n🌟 Popular areas: ${uni.popular_areas.join(', ')}\n\n${uni.description}\n\nWould you like me to search for hostels near ${uni.name}?`,
        data: uni,
        suggestions: [
          `Search hostels near ${uni.name}`,
          `Show hostels in ${uni.popular_areas[0]}`,
          `What's the average price in ${uni.popular_areas[1]}?`
        ]
      };
    } else {
      return {
        content: result.message,
        suggestions: ["Tell me about Makerere", "Tell me about Kyambogo", "Tell me about UCU"]
      };
    }
  };

  const handleAreaRequest = async (input) => {
    const area = extractArea(input);
    const areaTool = aiTools.find(tool => tool.name === 'get_area_info');
    const result = await areaTool.execute({ area });
    
    if (result.success) {
      const areaInfo = result.area;
      return {
        content: `📍 **${areaInfo.name}**\n\n🌍 Location: ${areaInfo.location}\n💰 Average price: UGX ${areaInfo.average_price.toLocaleString()}/month\n🛡️ Security: ${areaInfo.security_level}\n\n✨ Advantages:\n${areaInfo.advantages.map(adv => `• ${adv}`).join('\n')}\n\n🚗 Transport options: ${areaInfo.transport_options.join(', ')}\n\nPopular with: ${areaInfo.popular_with}\n\nWould you like me to search for hostels in ${areaInfo.name}?`,
        data: areaInfo,
        suggestions: [
          `Search hostels in ${areaInfo.name}`,
          `Show me budget options in ${areaInfo.name}`,
          `How safe is ${areaInfo.name} for students?`
        ]
      };
    } else {
      return {
        content: result.message,
        suggestions: ["Tell me about Kikoni", "Tell me about Wandegeya", "Tell me about Bwaise"]
      };
    }
  };

  const handleReservationRequest = async () => {
    return {
      content: "📋 I'd be happy to help you reserve a hostel! To get started, I'll need some information:\n\n🏠 Which hostel are you interested in?\n📅 When do you want to check in?\n📅 When do you want to check out?\n👥 How many guests?\n\nYou can tell me something like: \"I want to reserve [hostel name] from [date] to [date] for [number] guests\"\n\nOr if you haven't chosen a hostel yet, I can help you search first!",
      suggestions: [
        "Search for hostels first",
        "I want to reserve from next month",
        "Help me reserve for 2 guests",
        "What information do you need for reservation?"
      ]
    };
  };

  const handlePaymentRequest = async () => {
    const paymentTool = aiTools.find(tool => tool.name === 'get_payment_methods');
    const result = await paymentTool.execute({});
    
    if (result.success) {
      const paymentInfo = result.payment_methods.map(method => {
        if (method.name === 'Mobile Money') {
          const providers = method.providers.map(p => `📱 **${p.name}** - ${p.ussd} (Fee: ${p.fee})`).join('\n');
          return `💳 **${method.name}**\n${providers}`;
        } else if (method.name === 'Credit Cards') {
          const providers = method.providers.map(p => `💳 **${p.name}** - ${p.cards.join(', ')} (Fee: ${p.fee})`).join('\n');
          return `💳 **${method.name}**\n${providers}`;
        } else {
          const providers = method.providers.map(p => `💰 **${p.name}** - ${p.description} (Fee: ${p.fee})`).join('\n');
          return `💰 **${method.name}**\n${providers}`;
        }
      }).join('\n\n');
      
      return {
        content: `💳 **Payment Methods in Uganda**\n\n${paymentInfo}\n\n🇺🇬 **Mobile Money is most popular** - You can pay directly from your phone using USSD codes!\n\nNeed help with payment? Just ask me how to use any of these methods!`,
        suggestions: [
          "How do I pay with MTN MoMo?",
          "Can I pay with Airtel Money?",
          "Do you accept credit cards?",
          "What's the cheapest payment method?"
        ]
      };
    }
  };

  const handleTipsRequest = async (input) => {
    const topic = extractTopic(input);
    const tipsTool = aiTools.find(tool => tool.name === 'get_reservation_tips');
    const result = await tipsTool.execute({ topic });
    
    if (result.success) {
      const tipsList = result.tips.map(tip => `💡 ${tip}`).join('\n');
      return {
        content: `💡 **Helpful Tips for ${topic.charAt(0).toUpperCase() + topic.slice(1)}**\n\n${tipsList}\n\nThese tips will help you make better reservation decisions in Uganda!`,
        suggestions: [
          "Give me budget tips",
          "Tell me about safety tips",
          "What about location tips?",
          "Show me payment tips"
        ]
      };
    }
  };

  // Helper functions to extract information from user input
  const extractLocation = (input) => {
    const locations = ['kikoni', 'wandegeya', 'bwaise', 'mukono', 'mbarara', 'kampala'];
    const found = locations.find(loc => input.toLowerCase().includes(loc));
    return found || null;
  };

  const extractPrice = (input) => {
    const priceMatch = input.match(/(\d+)/);
    return priceMatch ? parseInt(priceMatch[1]) : null;
  };

  const extractUniversity = (input) => {
    const universities = ['makerere', 'kyambogo', 'bugema', 'ucu', 'must'];
    const found = universities.find(uni => input.toLowerCase().includes(uni));
    return found || null;
  };

  const extractArea = (input) => {
    const areas = ['kikoni', 'wandegeya', 'bwaise', 'mukono', 'mbarara'];
    const found = areas.find(area => input.toLowerCase().includes(area));
    return found || null;
  };

  const extractTopic = (input) => {
    const topics = ['budget', 'location', 'safety', 'payment'];
    const found = topics.find(topic => input.toLowerCase().includes(topic));
    return found || 'general';
  };

  const handleSendMessage = () => {
    if (inputValue.trim() && !isLoading) {
      processUserMessage(inputValue);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className={`enhanced-ai-assistant ${isOpen ? 'open' : ''}`}>
      {/* Toggle Button */}
      <button
        className="ai-assistant-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI Assistant"
      >
        <Bot className="w-6 h-6" />
        <span className="ai-badge">AI</span>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="ai-chat-window">
          {/* Header */}
          <div className="ai-chat-header">
            <div className="ai-header-info">
              <Bot className="w-5 h-5" />
              <div>
                <h3>RentHu Uganda AI</h3>
                <p>Your hostel reservation assistant</p>
              </div>
            </div>
            <button
              className="ai-close-btn"
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="ai-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.type}`}
              >
                <div className="message-avatar">
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-text">
                    {message.content}
                  </div>
                  {message.data && (
                    <div className="message-data">
                      {/* Render structured data here */}
                      {message.data.hostels && (
                        <div className="hostel-results">
                          {message.data.hostels.slice(0, 3).map((hostel, index) => (
                            <div key={index} className="hostel-card">
                              <h4>{hostel.name}</h4>
                              <p>{hostel.location}</p>
                              <p className="price">UGX {hostel.price?.toLocaleString()}/month</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">
                  <Bot className="w-4 h-4" />
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

          {/* Suggestions */}
          {suggestions.length > 0 && !isLoading && (
            <div className="ai-suggestions">
              <p className="suggestions-title">You might want to ask:</p>
              <div className="suggestions-list">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="ai-input-container">
            <div className="ai-input-wrapper">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about hostels, universities, or reservation..."
                className="ai-input"
                disabled={isLoading}
              />
              <button
                className="ai-send-btn"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            
            {/* Quick Actions */}
            <div className="ai-quick-actions">
              <button
                className="quick-action"
                onClick={() => handleSuggestionClick("Find hostels near Makerere")}
              >
                <MapPin className="w-4 h-4" />
                <span>Near Makerere</span>
              </button>
              <button
                className="quick-action"
                onClick={() => handleSuggestionClick("Show hostels under UGX 150,000")}
              >
                <DollarSign className="w-4 h-4" />
                <span>Under 150k</span>
              </button>
              <button
                className="quick-action"
                onClick={() => handleSuggestionClick("Help me reserve a room")}
              >
                <Book className="w-4 h-4" />
                <span>Reserve Now</span>
              </button>
              <button
                className="quick-action"
                onClick={() => handleSuggestionClick("Payment options")}
              >
                <CreditCard className="w-4 h-4" />
                <span>Payment</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAIAssistant;
