/**
 * ADA — Shared TypeScript Types and API Contracts
 * Shared across React Web Dashboard and React Native Mobile Companion.
 */

export type AutonomyMode = 'conversation' | 'assisted' | 'supervised' | 'bounded';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type DeviceType = 'desktop' | 'mobile' | 'web';

export type Platform = 'windows' | 'android' | 'ios' | 'web' | 'macos' | 'linux';

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export interface Device {
  id: string;
  user_id: string;
  device_type: DeviceType;
  display_name: string;
  platform: Platform;
  capabilities: string[];
  is_online?: boolean;
  last_seen_at?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  device_id?: string | null;
  title: string;
  summary?: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  user_id: string;
  role: MessageRole;
  content: string;
  content_type: string;
  tool_name?: string | null;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  device_id?: string | null;
  conversation_id?: string | null;
  title: string;
  description: string;
  tool_name: string;
  tool_args: Record<string, any>;
  priority: number;
  status: TaskStatus;
  result?: any;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApprovalRequest {
  id: string;
  user_id: string;
  task_id?: string | null;
  device_id?: string | null;
  tool_name: string;
  tool_args: Record<string, any>;
  risk_level: RiskLevel;
  reason: string;
  status: 'pending' | 'approved' | 'denied' | 'expired';
  created_at: string;
}

export interface Memory {
  id: string;
  user_id: string;
  content: string;
  category: string;
  importance: number;
  confidence: number;
  source: string;
  created_at: string;
}

// WebSocket message envelope
export interface WSMessage<T = any> {
  id?: string;
  type: string;
  payload: T;
}
