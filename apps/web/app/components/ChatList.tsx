/**
 * Chat List Component
 *
 * Displays list of conversations with selection and creation
 */

import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import { Conversation } from './conversation-types';

interface ChatListProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

export default function ChatList({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
}: ChatListProps) {
  return (
    <div className="chat-list">
      <div className="chat-list-header">
        <h3>Conversations</h3>
        <button
          className="new-chat-button"
          onClick={onCreateConversation}
          aria-label="New conversation"
          title="New conversation"
        >
          <Plus size={18} />
        </button>
      </div>

      {conversations.length === 0 ? (
        <div className="chat-list-empty">
          <MessageSquare size={32} />
          <p>No conversations yet</p>
          <p className="chat-list-empty-hint">Click + to start a new chat</p>
        </div>
      ) : (
        <ul className="chat-list-items">
          {conversations.map((conv) => (
            <li
              key={conv.id}
              className={`chat-list-item ${activeConversationId === conv.id ? 'active' : ''}`}
            >
              <button
                className="chat-list-item-button"
                onClick={() => onSelectConversation(conv.id)}
                aria-label={`Open conversation: ${conv.title}`}
                aria-current={activeConversationId === conv.id ? 'true' : undefined}
              >
                <div className="chat-list-item-content">
                  <div className="chat-list-item-title">{conv.title}</div>
                  <div className="chat-list-item-preview">
                    {conv.messages.length > 0 && conv.messages[conv.messages.length - 1]
                      ? conv.messages[conv.messages.length - 1]!.content.substring(0, 40) +
                        (conv.messages[conv.messages.length - 1]!.content.length > 40 ? '...' : '')
                      : 'No messages'}
                  </div>
                </div>
              </button>
              <button
                className="chat-list-item-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conv.id);
                }}
                aria-label={`Delete conversation: ${conv.title}`}
                title="Delete conversation"
              >
                <Trash2 size={14} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
