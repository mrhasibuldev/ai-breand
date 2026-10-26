/**
 * Conversation Types
 *
 * Types for conversation management
 */

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isError?: boolean;
  responseSource?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ConversationMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ConversationState {
  conversations: Map<string, Conversation>;
  activeConversationId: string | null;
}
