'use client';

/**
 * Chat Interface Component
 *
 * Simple clean chat interface with:
 * - Message history display
 * - Input field for user messages
 * - AI response display
 * - Typing indicator
 * - Supabase persistence
 *
 * @component
 */

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { Send, Zap } from 'lucide-react';
import { useConversationManager } from './useConversationManager';
import { ConversationMessage, Conversation } from './conversation-types';
import { useAuth } from './AuthContext';

/**
 * Chat Interface Component
 */
export default function ChatInterface() {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeRequestId, setActiveRequestId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const pendingMessageProcessed = useRef(false);

  // Local state for guest mode (in-memory only)
  const [guestConversations, setGuestConversations] = useState<Map<string, Conversation>>(new Map());
  const [guestActiveConversationId, setGuestActiveConversationId] = useState<string | null>(null);

  // Auth and conversation manager
  const { isAuthenticated, user } = useAuth();
  const {
    activeConversationId,
    createConversation,
    addMessage,
    getActiveConversation,
    setConversations,
    loading: conversationLoading,
  } = useConversationManager();

  // Handle pending message from homepage navigation
  useEffect(() => {
    if (pendingMessageProcessed.current) return;

    const pendingMessage = localStorage.getItem('nexusai_pending_message');
    if (pendingMessage) {
      console.log('[ChatInterface] Found pending message from homepage:', pendingMessage);
      localStorage.removeItem('nexusai_pending_message');
      pendingMessageProcessed.current = true;
      
      // For guest users, submit immediately (no conversation needed)
      if (!isAuthenticated) {
        setTimeout(() => {
          handleGuestMessage(pendingMessage);
        }, 100);
      } else {
        // Authenticated flow - set input and it will auto-submit when ready
        setInputValue(pendingMessage);
      }
    }
  }, [isAuthenticated]);

  // Auto-submit pending message for authenticated users when conversation manager is ready
  useEffect(() => {
    if (!pendingMessageProcessed.current || !inputValue.trim() || !isAuthenticated) return;
    
    // Wait for conversation loading to complete before submitting
    if (conversationLoading) return;
    
    // Don't submit if already typing (means we already started processing)
    if (isTyping) return;
    
    // Submit the pending message after a short delay to ensure component is ready
    setTimeout(() => {
      const formEvent = new Event('submit', { cancelable: true }) as any;
      handleSubmit(formEvent);
    }, 200);
  }, [isAuthenticated, inputValue, conversationLoading, isTyping]);

  // Get active conversation (guest if not authenticated)
  const activeConversation = useMemo(() => {
    if (isAuthenticated) {
      return getActiveConversation();
    }
    return guestActiveConversationId ? guestConversations.get(guestActiveConversationId) : null;
  }, [isAuthenticated, getActiveConversation, guestActiveConversationId, guestConversations]);



  /**
   * Auto-scroll to bottom when messages change - use stable dependencies
   */
  const messagesLength = activeConversation?.messages.length || 0;
  
  useEffect(() => {
    if (activeConversation && messagesLength > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messagesLength, activeConversation]); // Only depends on message count

  /**
   * Handle input change with debounced state update
   */
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  }, []);

  /**
   * Handle message submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // If typing, treat as cancel
    if (isTyping) {
      handleCancelRequest();
      return;
    }

    if (!inputValue.trim()) return;

    const message = inputValue;
    console.log('[ChatInterface] Submitting message, authenticated:', isAuthenticated, 'activeConversationId:', activeConversationId);

    // For guest mode, use in-memory state
    if (!isAuthenticated) {
      setInputValue(''); // Clear input after we know we're processing
      await handleGuestMessage(message);
      return;
    }

    // For authenticated users, use Supabase persistence
    let convId = activeConversationId;
    if (!convId) {
      try {
        console.log('[ChatInterface] Creating new conversation...');
        convId = await createConversation(message);
        console.log('[ChatInterface] Conversation created, ID:', convId);
      } catch (error) {
        console.error('[ChatInterface] Error creating conversation:', error);
        // Show error to user
        return;
      }
    }

    if (convId) {
      setInputValue(''); // Clear input only after we have a valid conversation
      await handleSendMessage(message, convId);
    } else {
      console.error('[ChatInterface] Failed to create conversation - conversation ID is null');
      // Input not cleared so user can retry
    }
  };

  /**
   * Handle guest message (in-memory only, no persistence)
   */
  const handleGuestMessage = async (userMessage: string) => {
    const requestId = `NEXUSAI_REQ_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    setActiveRequestId(requestId);
    setIsTyping(true);
    console.log(`[ChatInterface] Guest request ${requestId}`);

    // Abort previous request if exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const userMsg: ConversationMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    };

    // Add to guest conversation state
    setGuestConversations(prev => {
      const guestConvId = 'guest';
      const existing = prev.get(guestConvId);
      if (existing) {
        return new Map(prev).set(guestConvId, {
          ...existing,
          messages: [...existing.messages, userMsg],
          updatedAt: new Date(),
        });
      }
      return new Map(prev).set(guestConvId, {
        id: guestConvId,
        title: 'Guest Chat',
        messages: [userMsg],
        createdAt: new Date(),
        updatedAt: new Date(),
      });
    });
    setGuestActiveConversationId('guest');

    try {
      const response = await fetch('http://localhost:4000/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          message: userMessage,
          conversationId: 'guest',
          context: [],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        
        // Distinguish between different error types
        if (response.status === 502) {
          throw new Error('AI service unavailable');
        } else if (response.status === 504) {
          throw new Error('AI service timeout');
        } else if (response.status === 500) {
          throw new Error('Backend server error');
        } else if (response.status === 401) {
          throw new Error('Authentication required');
        } else {
          throw new Error(errorData.error || 'AI service error');
        }
      }

      const data = await response.json();
      console.log(`[ChatInterface] Guest request ${requestId} completed`);

      const aiMessage: ConversationMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        responseSource: data.response_source,
      };

      setGuestConversations(prev => {
        const existing = prev.get('guest');
        if (existing) {
          return new Map(prev).set('guest', {
            ...existing,
            messages: [...existing.messages, aiMessage],
            updatedAt: new Date(),
          });
        }
        return prev;
      });
    } catch (error) {
      console.error('[ChatInterface] Guest request failed:', error);

      // Determine error type and show appropriate message
      let errorMessage: string;

      if (error instanceof Error) {
        if (error.message === 'AI service unavailable') {
          errorMessage = "দুঃখিত, AI সার্ভিসটি বর্তমানে উপলব্ধ নেই। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'AI service timeout') {
          errorMessage = "দুঃখিত, AI সার্ভিসটি সময়সীমা অতিক্রম করেছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'Backend server error') {
          errorMessage = "দুঃখিত, সার্ভারে একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'Authentication required') {
          errorMessage = "দুঃখিত, আপনার সেশন মেয়াদ শেষ হয়েছে। অনুগ্রহ করে আবার লগ ইন করুন।";
        } else if (error.message === 'Request timeout') {
          errorMessage = "দুঃখিত, অনুরোধ সময় শেষ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
        } else if (error.message.includes('fetch') || error.message.includes('NetworkError')) {
          errorMessage = "দুঃখিত, সিস্টেম ব্যাকএন্ডের সাথে যোগাযোগ করতে সমস্যা হচ্ছে। অনুগ্রহ করে সার্ভিসটি চালু আছে কিনা পরীক্ষা করুন।";
        } else {
          errorMessage = "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
        }
      } else {
        errorMessage = "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
      }
      const errorObj: ConversationMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
        isError: true,
      };
      setGuestConversations(prev => {
        const existing = prev.get('guest');
        if (existing) {
          return new Map(prev).set('guest', {
            ...existing,
            messages: [...existing.messages, errorObj],
            updatedAt: new Date(),
          });
        }
        return prev;
      });
    } finally {
      setIsTyping(false);
      setActiveRequestId(null);
    }
  };

  /**
   * Send message to brain service (authenticated mode with persistence)
   */
  const handleSendMessage = async (userMessage: string, conversationId: string) => {
    // Prevent duplicate requests
    if (activeRequestId) {
      console.log('[ChatInterface] Request already active, ignoring duplicate submission');
      return;
    }

    // Generate unique request ID
    const requestId = `NEXUSAI_REQ_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    setActiveRequestId(requestId);
    setIsTyping(true);
    console.log(`[ChatInterface] Starting request ${requestId} for conversation ${conversationId}`);

    // Abort previous request if exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    // Get conversation history for context
    const activeConv = getActiveConversation();
    const conversationHistory = activeConv ? activeConv.messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp.toISOString()
    })) : [];

    try {
      // Persist user message first
      const userMsg: ConversationMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      };
      await addMessage(conversationId, userMsg);

      // Call backend AI service
      const response = await fetch('http://localhost:4000/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          message: userMessage,
          conversationId,
          context: conversationHistory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        
        // Distinguish between different error types
        if (response.status === 502) {
          throw new Error('AI service unavailable');
        } else if (response.status === 504) {
          throw new Error('AI service timeout');
        } else if (response.status === 500) {
          throw new Error('Backend server error');
        } else if (response.status === 401) {
          throw new Error('Authentication required');
        } else {
          throw new Error(errorData.error || 'AI service error');
        }
      }

      const data = await response.json();
      console.log(`[ChatInterface] Request ${requestId} completed successfully`);

      // Add assistant message to conversation
      const aiMessage: ConversationMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      await addMessage(conversationId, aiMessage);
    } catch (error) {
      console.log(`[ChatInterface] Request ${requestId} failed:`, error);

      // Determine error type and show appropriate message
      let errorMessage: string;

      if (error instanceof Error) {
        if (error.message === 'AI service unavailable') {
          errorMessage = "দুঃখিত, AI সার্ভিসটি বর্তমানে উপলব্ধ নেই। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'AI service timeout') {
          errorMessage = "দুঃখিত, AI সার্ভিসটি সময়সীমা অতিক্রম করেছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'Backend server error') {
          errorMessage = "দুঃখিত, সার্ভারে একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।";
        } else if (error.message === 'Authentication required') {
          errorMessage = "দুঃখিত, আপনার সেশন মেয়াদ শেষ হয়েছে। অনুগ্রহ করে আবার লগ ইন করুন।";
        } else if (error.message === 'Request timeout') {
          errorMessage = "দুঃখিত, অনুরোধ সময় শেষ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
        } else if (error.message.includes('fetch') || error.message.includes('NetworkError')) {
          errorMessage = "দুঃখিত, সিস্টেম ব্যাকএন্ডের সাথে যোগাযোগ করতে সমস্যা হচ্ছে। অনুগ্রহ করে সার্ভিসটি চালু আছে কিনা পরীক্ষা করুন।";
        } else {
          errorMessage = "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
        }
      } else {
        errorMessage = "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।";
      }

      // Show error message in UI (not persisted to database)
      const errorObj: ConversationMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
        isError: true,
      };

      // Add error message only to local state (not database)
      setConversations(prev => {
        const conv = prev.get(conversationId);
        if (!conv) return prev;

        const updated = {
          ...conv,
          messages: [...conv.messages, errorObj],
          updatedAt: new Date(),
        };

        return new Map(prev).set(conversationId, updated);
      });
    } finally {
      setIsTyping(false);
      setActiveRequestId(null);
      console.log(`[ChatInterface] Request ${requestId} cleanup complete`);
    }
  };

  /**
   * Cancel active request
   */
  const handleCancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      console.log('[ChatInterface] Request cancelled by user');
    }
  };

  return (
    <div className="chat-container">
      {/* Messages Area */}
      <div className="chat-messages">
        {!activeConversation && (
          <div className="chat-empty">
            <div className="empty-icon">
              <Zap size={48} />
            </div>
            <h2>Welcome to NexusAI</h2>
            <p>Your intelligent AI assistant</p>
            <p className="chat-empty-hint">
              {isAuthenticated ? "Start a conversation below" : "Guest mode - chats won't be saved. Sign in to save your history."}
            </p>
          </div>
        )}

        {activeConversation && activeConversation.messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.role === 'user' ? 'user' : 'assistant'} ${message.isError ? 'error' : ''}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? (
                <div style={{ color: 'white', fontWeight: 600, fontSize: '14px' }}>
                  U
                </div>
              ) : (
                <Zap size={20} style={{ color: 'var(--accent-primary)' }} />
              )}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat-message assistant">
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
              onChange={handleInputChange}
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
              aria-label={isTyping ? "Cancel request" : "Send message"}
              title={isTyping ? "Cancel request" : "Send message"}
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
