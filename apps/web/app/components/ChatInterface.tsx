'use client';

/**
 * Chat Interface Component
 *
 * Displays the chat interface for NexusData AI with:
 * - Message history display
 * - Input field for user messages
 * - AI response display
 * - Typing indicator
 *
 * @component
 */

import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Zap } from 'lucide-react';

/**
 * Message interface
 */
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

/**
 * Chat Interface Component
 */
export default function ChatInterface({ initialMessage }: { initialMessage?: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Handle initial message from home page
   */
  useEffect(() => {
    if (initialMessage && initialMessage.trim()) {
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: initialMessage,
        timestamp: new Date(),
      };

      setMessages([userMessage]);
      setInputValue('');
      setIsTyping(true);

      setTimeout(() => {
        const aiMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: generateAIResponse(userMessage.content),
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000);
    }
  }, [initialMessage]);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handle message submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response (will be replaced with actual AI)
    setTimeout(() => {
      const aiMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: generateAIResponse(userMessage.content),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  /**
   * Generate AI response (simple rule-based for now)
   * This will be replaced with actual NexusData AI
   */
  const generateAIResponse = (userInput: string): string => {
    const lowerInput = userInput.toLowerCase();

    // Simple rule-based responses
    if (lowerInput.includes('hello') || lowerInput.includes('hi')) {
      return 'Hello! I am NexusData, your personal AI assistant. How can I help you today?';
    }

    if (lowerInput.includes('how are you')) {
      return 'I am functioning optimally! Thank you for asking. How can I assist you?';
    }

    if (lowerInput.includes('name')) {
      return 'My name is NexusData. I am a custom AI designed to help you with various tasks.';
    }

    if (lowerInput.includes('help')) {
      return 'I can help you with:\n- Chatting and answering questions\n- Creating images\n- Assisting with wellness goals\n- Providing information\n\nWhat would you like to do?';
    }

    if (lowerInput.includes('image') || lowerInput.includes('create')) {
      return 'I can help you create images! Please describe what kind of image you would like me to generate, and I will do my best to create it for you.';
    }

    // Default response
    return 'I understand your message. As NexusData, I am continuously learning to provide better responses. Let me think about that...';
  };

  return (
    <div className="chat-container">
      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <Bot size={48} />
            </div>
            <h2>Welcome to NexusData</h2>
            <p>Your personal AI assistant</p>
            <p className="chat-empty-hint">
              Start a conversation by typing a message below
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.role === 'user' ? 'user' : 'assistant'}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? (
                <User size={20} />
              ) : (
                <Bot size={20} />
              )}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat-message assistant">
            <div className="message-avatar">
              <Bot size={20} />
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

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit}>
          <div className="chat-input-wrapper">
            <div className="chat-input-icon">
              <Zap size={20} />
            </div>
            <textarea
              className="chat-input"
              placeholder="Type your message to NexusData..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              className="chat-send-button"
              disabled={!inputValue.trim() || isTyping}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
