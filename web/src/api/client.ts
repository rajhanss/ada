import type {
  Conversation,
  Message,
  Task,
  ApprovalRequest,
  Device,
  AutonomyMode,
} from '../../../shared/contracts/types';

const API_BASE = '/api/v1';

class AdaApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('ada_jwt_token', token);
  }

  getToken(): string {
    if (!this.token) {
      this.token = localStorage.getItem('ada_jwt_token') || 'demo_dev_token';
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.getToken()}`,
      ...(options.headers || {}),
    };

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`API Error ${res.status}: ${err}`);
    }

    return res.json();
  }

  // Health
  async getHealth() {
    return fetch('/health').then((r) => r.json());
  }

  // Conversations
  async listConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/conversations');
  }

  async createConversation(title: string, device_id?: string): Promise<Conversation> {
    return this.request<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title, device_id }),
    });
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    return this.request<Message[]>(`/conversations/${conversationId}/messages`);
  }

  async sendMessage(
    conversationId: string,
    content: string,
    autonomyMode: AutonomyMode = 'supervised'
  ): Promise<Message> {
    return this.request<Message>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, autonomy_mode: autonomyMode }),
    });
  }

  // Tasks
  async listTasks(): Promise<Task[]> {
    return this.request<Task[]>('/tasks');
  }

  async createTask(params: {
    title: string;
    description: string;
    tool_name: string;
    tool_args: Record<string, any>;
    device_id?: string;
  }): Promise<Task> {
    return this.request<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Approvals
  async listApprovals(): Promise<ApprovalRequest[]> {
    return this.request<ApprovalRequest[]>('/approvals');
  }

  async resolveApproval(approvalId: string, approved: boolean): Promise<void> {
    return this.request<void>(`/approvals/${approvalId}/${approved ? 'approve' : 'deny'}`, {
      method: 'POST',
    });
  }

  // Devices
  async listDevices(): Promise<Device[]> {
    return this.request<Device[]>('/devices');
  }
}

export const api = new AdaApiClient();
