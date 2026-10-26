'use client';

/**
 * History Page Component
 *
 * Displays user's conversation history from Supabase
 * Allows selecting and opening old conversations
 */

import { useState, useEffect } from 'react';
import { Clock, MessageSquare, Plus } from 'lucide-react';
import { useAuth } from './AuthContext';
import { useConversationManager } from './useConversationManager';

export interface Conversation {
  id: string;
  title: string;
  messages: ConversationMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ConversationMessage {
  id: string;
  role: string;
  content: string;
  timestamp: Date;
}

export default function HistoryPage({
  onNavChange,
}: {
  onNavChange: (nav: string) => void;
}) {
  const { isAuthenticated } = useAuth();
  const { conversations, selectConversation, createConversation, loading, loadConversationsFromBackend } = useConversationManager();
  const [conversationsArray, setConversationsArray] = useState<Conversation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [displayCount, setDisplayCount] = useState(10); // Pagination: show 10 at a time

  // Convert Map to array and sort by recent activity
  useEffect(() => {
    const array = Array.from(conversations.values()).sort(
      (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
    );
    setConversationsArray(array);
  }, [conversations]);

  // Get conversations to display (pagination)
  const displayedConversations = conversationsArray.slice(0, displayCount);
  const hasMore = conversationsArray.length > displayCount;

  // Retry loading conversations
  const handleRetry = async () => {
    setError(null);
    try {
      await loadConversationsFromBackend();
    } catch {
      setError('Failed to load conversations. Please try again.');
    }
  };

  const handleSelectConversation = async (id: string) => {
    await selectConversation(id);
    onNavChange('chat');
  };

  const handleNewChat = async () => {
    const convId = await createConversation('New Chat');
    if (convId) {
      onNavChange('chat');
    }
  };

  const handleLoadMore = () => {
    setDisplayCount(prev => prev + 10);
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (!isAuthenticated) {
    return (
      <div className="content-area">
        <div className="empty-state">
          <Clock size={48} className="empty-icon" />
          <h2>Sign in to view history</h2>
          <p>Your conversation history will appear here after you sign in.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="content-area">
        <div className="loading-state">
          <p>Loading conversations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content-area">
        <div className="empty-state">
          <MessageSquare size={48} className="empty-icon" />
          <h2>Error loading conversations</h2>
          <p>{error}</p>
          <button onClick={handleRetry} className="primary-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (conversationsArray.length === 0) {
    return (
      <div className="content-area">
        <div className="empty-state">
          <MessageSquare size={48} className="empty-icon" />
          <h2>No conversations yet</h2>
          <p>Start a new conversation to see it here.</p>
          <button onClick={handleNewChat} className="primary-button">
            <Plus size={20} />
            New Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="content-area">
      <div className="history-page">
        <div className="history-header">
          <h1>Conversation History</h1>
          <button onClick={handleNewChat} className="primary-button">
            <Plus size={20} />
            New Chat
          </button>
        </div>

        <div className="history-list">
          {displayedConversations.map((conv) => (
            <div
              key={conv.id}
              className="history-item"
              onClick={() => handleSelectConversation(conv.id)}
            >
              <div className="history-item-icon">
                <MessageSquare size={20} />
              </div>
              <div className="history-item-content">
                <div className="history-item-title">{conv.title}</div>
                <div className="history-item-meta">
                  <span className="history-item-date">{formatDate(conv.updatedAt)}</span>
                  <span className="history-item-messages">
                    {conv.messages.length} messages
                  </span>
                </div>
              </div>
            </div>
          ))}
          {hasMore && (
            <button
              onClick={handleLoadMore}
              className="load-more-button"
            >
              Load More ({conversationsArray.length - displayCount} remaining)
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
