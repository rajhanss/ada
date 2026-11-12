import type {
  Conversation,
  Message,
  Task,
  ApprovalRequest,
  Device,
  AutonomyMode,
} from '../../shared/contracts/types';

// Mobile API client
// In local dev/testing on Android emulator, 10.0.2.2 points to host localhost:8000
// On real devices, points to your LAN IP or deployed backend URL
const DEFAULT_HOST = 'http://10.0.2.2:8000/api/v1';

export class MobileApiClient {
  private baseUrl: string = DEFAULT_HOST;
  private token: string = 'demo_mobile_token';

  setBaseUrl(url: string) {
    this.baseUrl = url.replace(/\/$/, '') + '/api/v1';
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.token}`,
      ...(options.headers || {}),
    };

    const res = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`API Error ${res.status}: ${err}`);
    }

    return res.json();
  }

  async listConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/conversations');
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

  async listTasks(): Promise<Task[]> {
    return this.request<Task[]>('/tasks');
  }

  async listApprovals(): Promise<ApprovalRequest[]> {
    return this.request<ApprovalRequest[]>('/approvals');
  }

  async resolveApproval(approvalId: string, approved: boolean): Promise<void> {
    return this.request<void>(`/approvals/${approvalId}/${approved ? 'approve' : 'deny'}`, {
      method: 'POST',
    });
  }

  async listDevices(): Promise<Device[]> {
    return this.request<Device[]>('/devices');
  }
}

export const mobileApi = new MobileApiClient();
