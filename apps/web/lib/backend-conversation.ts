/**
 * Backend Conversation Service
 *
 * Handles conversation operations using the backend API
 */

const API_BASE = process.env.NEXT_PUBLIC_API_ORIGIN || 'http://localhost:4000';
const REQUEST_TIMEOUT = 15000; // 15 seconds

export interface Conversation {
  id: string;
  account_id: string;
  title: string;
  status: 'active' | 'ended' | 'deleted';
  started_at: string;
  ended_at: string | null;
  deleted_at: string | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface CreateConversationInput {
  title?: string;
}

export interface CreateMessageInput {
  senderRole: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = REQUEST_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

/**
 * List user's conversations
 */
export async function listConversations(): Promise<Conversation[]> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/conversations`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to list conversations');
  }

  return response.json();
}

/**
 * Get specific conversation with messages
 */
export async function getConversation(id: string): Promise<{ conversation: Conversation; messages: Message[] } | null> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/conversations/${id}`, {
    method: 'GET',
    credentials: 'include',
  });

  if (response.status === 404) {
    return null; // Conversation not found
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get conversation');
  }

  return response.json();
}

/**
 * Create a new conversation
 */
export async function createConversation(input: CreateConversationInput): Promise<Conversation> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create conversation');
  }

  return response.json();
}

/**
 * Add message to conversation
 */
export async function createMessage(conversationId: string, input: CreateMessageInput): Promise<Message> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create message');
  }

  return response.json();
}

/**
 * Delete conversation
 */
export async function deleteConversation(id: string): Promise<boolean> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/conversations/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (response.status === 404) {
    return false; // Conversation not found
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to delete conversation');
  }

  return response.status === 204;
}
