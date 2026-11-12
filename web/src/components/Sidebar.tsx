import React from 'react';
import {
  MessageSquare,
  ListTodo,
  ShieldAlert,
  Laptop,
  Brain,
  Radio,
} from 'lucide-react';

export type TabType = 'chat' | 'tasks' | 'approvals' | 'devices' | 'memory';

interface SidebarProps {
  currentTab: TabType;
  onTabChange: (tab: TabType) => void;
  pendingApprovalsCount: number;
  wsConnected: boolean;
}

interface NavItem {
  id: TabType;
  label: string;
  icon: any;
  badge?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  pendingApprovalsCount,
  wsConnected,
}) => {
  const navItems: NavItem[] = [
    { id: 'chat', label: 'Chat & Actions', icon: MessageSquare },
    { id: 'tasks', label: 'Task Monitor', icon: ListTodo },
    {
      id: 'approvals',
      label: 'Authorizations',
      icon: ShieldAlert,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: 'devices', label: 'Connected Devices', icon: Laptop },
    { id: 'memory', label: 'Memory & State', icon: Brain },
  ];

  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 16px',
    }}>
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
        <div
          className="orb-pulse"
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: 'var(--ada-saffron)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px var(--ada-saffron-glow)',
          }}
        >
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FFF' }} />
        </div>
        <div>
          <h1 style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '0.02em', color: '#FFF' }}>
            ADA
          </h1>
          <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '-2px' }}>
            Autonomous Digital Assistant
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id as TabType)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 12px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: isActive ? 'var(--bg-card-hover)' : 'transparent',
                color: isActive ? 'var(--ada-saffron)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 500,
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={18} color={isActive ? 'var(--ada-saffron)' : 'var(--text-secondary)'} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge !== undefined && (
                <span
                  style={{
                    backgroundColor: 'var(--status-warning)',
                    color: '#000',
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '2px 7px',
                    borderRadius: '10px',
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Connection Pill */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '10px 12px',
          backgroundColor: 'var(--bg-card)',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <Radio
          size={14}
          color={wsConnected ? 'var(--status-success)' : 'var(--status-danger)'}
        />
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          {wsConnected ? 'Cloud Sync Online' : 'Connecting Sync...'}
        </span>
      </div>
    </aside>
  );
};
