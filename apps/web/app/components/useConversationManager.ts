/**
 * Conversation Manager Hook
 *
 * Manages conversation state with backend API persistence
 * React state is used for UI rendering, backend API is source of truth
 */

import { useState, useCallback, useEffect } from 'react';
import { Conversation, ConversationMessage } from './conversation-types';
import { useAuth } from './AuthContext';
import * as backendConversationService from '../../lib/backend-conversation';

export function useConversationManager() {
  const [conversations, setConversations] = useState<Map<string, Conversation>>(new Map());
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // Local storage key for last active conversation
  const LAST_ACTIVE_CONV_KEY = 'nexusai_last_active_conversation';

  /**
   * Load conversations from backend
   */
  const loadConversationsFromBackend = useCallback(async () => {
    if (!isAuthenticated) {
      console.log('[ConversationManager] Not authenticated, skipping load');
      return;
    }

    setLoading(true);
    try {
      const backendConversations = await backendConversationService.listConversations();

      // Convert backend conversations to local format
      const convMap = new Map<string, Conversation>();
      for (const conv of backendConversations) {
        convMap.set(conv.id, {
          id: conv.id,
          title: conv.title,
          messages: [], // Messages loaded separately
          createdAt: new Date(conv.started_at),
          updatedAt: conv.ended_at ? new Date(conv.ended_at) : new Date(conv.started_at),
        });
      }

      setConversations(convMap);
      console.log('[ConversationManager] Loaded conversations from backend:', convMap.size);

      // Restore last active conversation from localStorage
      try {
        const lastActiveId = localStorage.getItem(LAST_ACTIVE_CONV_KEY);
        if (lastActiveId && convMap.has(lastActiveId)) {
          setActiveConversationId(lastActiveId);
          console.log('[ConversationManager] Restored last active conversation:', lastActiveId);
          // Load messages for the restored conversation (will be loaded separately)
        }
      } catch (e) {
        console.warn('[ConversationManager] Failed to restore last active conversation:', e);
      }
    } catch (error) {
      console.error('[ConversationManager] Failed to load conversations:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  /**
   * Load messages for a specific conversation
   */
  const loadMessagesForConversation = useCallback(async (conversationId: string) => {
    if (!isAuthenticated) {
      console.log('[ConversationManager] Not authenticated, skipping message load');
      return;
    }

    try {
      const conversationData = await backendConversationService.getConversation(conversationId);
      
      if (!conversationData) {
        console.warn('[ConversationManager] Conversation not found:', conversationId);
        return;
      }

      // Convert backend messages to local format
      const messages: ConversationMessage[] = conversationData.messages.map(msg => ({
        id: msg.id,
        role: msg.sender_role,
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));
      
      setConversations(prev => {
        const conv = prev.get(conversationId);
        if (!conv) return prev;
        
        const updated = {
          ...conv,
          messages,
        };
        
        return new Map(prev).set(conversationId, updated);
      });
      
      console.log('[ConversationManager] Loaded messages:', messages.length);
    } catch (error) {
      console.error('[ConversationManager] Failed to load messages:', error);
    }
  }, [isAuthenticated]);

  /**
   * Load conversations on mount when authenticated
   */
  useEffect(() => {
    if (isAuthenticated) {
      loadConversationsFromBackend();
    } else {
      // Clear conversations when logged out
      setConversations(new Map());
      setActiveConversationId(null);
      localStorage.removeItem(LAST_ACTIVE_CONV_KEY);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  /**
   * Save last active conversation to localStorage
   */
  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem(LAST_ACTIVE_CONV_KEY, activeConversationId);
    }
  }, [activeConversationId]);

  /**
   * Create a new conversation in backend
   */
  const createConversation = useCallback(async (initialMessage?: string): Promise<string | null> => {
    if (!isAuthenticated) {
      console.error('[ConversationManager] Cannot create conversation: not authenticated');
      throw new Error('Not authenticated');
    }

    const title = initialMessage
      ? initialMessage.substring(0, 30) + (initialMessage.length > 30 ? '...' : '')
      : 'New Conversation';

    try {
      const backendConv = await backendConversationService.createConversation({ title });

      // Add to local state
      const newConversation: Conversation = {
        id: backendConv.id,
        title: backendConv.title,
        messages: [],
        createdAt: new Date(backendConv.started_at),
        updatedAt: new Date(backendConv.started_at),
      };

      setConversations(prev => new Map(prev).set(backendConv.id, newConversation));
      setActiveConversationId(backendConv.id);

      return backendConv.id;
    } catch (error) {
      console.error('[ConversationManager] Error creating conversation:', error);
      throw error;
    }
  }, [isAuthenticated]);

  /**
   * Select a conversation and load its messages
   */
  const selectConversation = useCallback(async (id: string) => {
    setActiveConversationId(id);
    await loadMessagesForConversation(id);
  }, []);

  /**
   * Delete a conversation
   */
  const deleteConversation = useCallback(async (id: string) => {
    if (!isAuthenticated) {
      console.error('[ConversationManager] Cannot delete conversation: not authenticated');
      return;
    }

    const success = await backendConversationService.deleteConversation(id);
    
    if (success) {
      setConversations(prev => {
        const newMap = new Map(prev);
        newMap.delete(id);
        return newMap;
      });
      
      if (activeConversationId === id) {
        setActiveConversationId(null);
      }
    }
  }, [activeConversationId, isAuthenticated]);

  /**
   * Add a message to a conversation (persist to backend)
   */
  const addMessage = useCallback(async (conversationId: string, message: ConversationMessage) => {
    if (!isAuthenticated) {
      console.error('[ConversationManager] Cannot add message: not authenticated');
      throw new Error('Not authenticated');
    }

    // Add to local state first for immediate UI feedback
    setConversations(prev => {
      const conv = prev.get(conversationId);
      if (!conv) return prev;

      const updated = {
        ...conv,
        messages: [...conv.messages, message],
        updatedAt: new Date(),
      };

      return new Map(prev).set(conversationId, updated);
    });

    // Persist to backend
    try {
      const backendMessage = await backendConversationService.createMessage(
        conversationId,
        {
          senderRole: message.role,
          content: message.content
        }
      );

      console.log('[ConversationManager] Message persisted to backend:', backendMessage.id);
    } catch (error) {
      console.error('[ConversationManager] Error adding message:', error);
      throw error;
    }
  }, [isAuthenticated]);

  /**
   * Get active conversation
   */
  const getActiveConversation = useCallback((): Conversation | null => {
    if (!activeConversationId) return null;
    return conversations.get(activeConversationId) || null;
  }, [activeConversationId, conversations]);

  /**
   * Get all conversations as array
   */
  const getConversationsArray = useCallback((): Conversation[] => {
    return Array.from(conversations.values()).sort(
      (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
    );
  }, [conversations]);

  return {
    conversations,
    activeConversationId,
    loading,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
    getActiveConversation,
    getConversationsArray,
    loadConversationsFromBackend,
    setConversations,
  };
}
