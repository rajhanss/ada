import React from 'react';
import {
  MessageSquare,
  ListTodo,
  ShieldAlert,
  Laptop,
  Brain,
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
    { id: 'chat', label: 'Chat & actions', icon: MessageSquare },
    { id: 'tasks', label: 'Task monitor', icon: ListTodo },
    {
      id: 'approvals',
      label: 'Authorizations',
      icon: ShieldAlert,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: 'devices', label: 'Connected devices', icon: Laptop },
    { id: 'memory', label: 'Memory & state', icon: Brain },
  ];

  return (
    <aside
      style={{
        width: '240px',
        height: '100vh',
        backgroundColor: 'var(--ada-bg-sidebar)',
        borderRight: '1px solid var(--ada-border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px 16px',
      }}
    >
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: '4px',
            backgroundColor: 'var(--ada-saffron)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--ada-text-main)',
            fontWeight: 800,
            fontSize: '13px',
            fontFamily: 'var(--ada-font-mono)',
          }}
        >
          A
        </div>
        <div>
          <h1 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--ada-text-main)' }}>
            ADA
          </h1>
          <p style={{ fontSize: '11px', color: 'var(--ada-text-dim)', marginTop: '-2px' }}>
            Autonomous OS
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onTabChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: isActive ? 'var(--ada-bg-card)' : 'transparent',
                color: isActive ? 'var(--ada-text-main)' : 'var(--ada-text-secondary)',
                fontWeight: isActive ? 600 : 400,
                fontSize: '13px',
                cursor: 'pointer',
                fontFamily: 'var(--ada-font-sans)',
                textAlign: 'left',
                width: '100%',
                transition: 'background-color 0.15s ease, color 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Icon
                  size={16}
                  color={isActive ? 'var(--ada-saffron)' : 'var(--ada-text-dim)'}
                  aria-hidden="true"
                />
                <span>{item.label}</span>
              </div>

              {item.badge !== undefined && (
                <span
                  style={{
                    backgroundColor: 'var(--ada-status-warning)',
                    color: 'var(--ada-bg-app)',
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '1px 6px',
                    borderRadius: '10px',
                    fontFamily: 'var(--ada-font-mono)',
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Connection Status Footer */}
      <div
        style={{
          paddingTop: '16px',
          borderTop: '1px solid var(--ada-border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: 'var(--ada-text-dim)',
          fontFamily: 'var(--ada-font-mono)',
        }}
      >
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: wsConnected ? 'var(--ada-status-success)' : 'var(--ada-status-danger)',
          }}
        />
        <span>{wsConnected ? 'WebSocket connected' : 'Connecting to daemon...'}</span>
      </div>
    </aside>
  );
};
