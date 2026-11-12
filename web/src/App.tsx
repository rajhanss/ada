import React, { useState } from 'react';
import { Sidebar, type TabType } from './components/Sidebar';
import { ChatPage } from './pages/ChatPage';
import { TasksPage } from './pages/TasksPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { DevicesPage } from './pages/DevicesPage';
import { LandingPage } from './pages/LandingPage';
import { DynamicIsland } from './components/DynamicIsland';
import { useAdaWebSocket } from './hooks/useAdaWebSocket';
import { Globe } from 'lucide-react';

export const App: React.FC = () => {
  const [view, setView] = useState<'app' | 'landing'>('landing');
  const [currentTab, setCurrentTab] = useState<TabType>('chat');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState(1);
  const { isConnected } = useAdaWebSocket();

  if (view === 'landing') {
    return <LandingPage onLaunchWebApp={() => setView('app')} />;
  }

  const renderContent = () => {
    switch (currentTab) {
      case 'chat':
        return <ChatPage />;
      case 'tasks':
        return <TasksPage />;
      case 'approvals':
        return (
          <ApprovalsPage
            onApprovalResolved={() => setPendingApprovalsCount((c) => Math.max(0, c - 1))}
          />
        );
      case 'devices':
        return <DevicesPage />;
      case 'memory':
        return (
          <div style={{ padding: '32px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px', color: 'var(--ada-text-main)' }}>
              Persistent memory and state
            </h2>
            <p style={{ color: 'var(--ada-text-secondary)', fontSize: '13px' }}>
              Inspect long-term preferences, workstation knowledge, and verified automation workflows.
            </p>
          </div>
        );
      default:
        return <ChatPage />;
    }
  };

  return (
    <div style={{ display: 'flex', width: '100%', height: '100vh', overflow: 'hidden', position: 'relative' }}>
      <DynamicIsland onActionTriggered={(action) => console.log('Action triggered:', action)} />

      {/* View Switcher Button */}
      <button
        type="button"
        onClick={() => setView('landing')}
        style={{
          position: 'fixed',
          top: '16px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: 'var(--ada-bg-card)',
          border: '1px solid var(--ada-border-strong)',
          color: 'var(--ada-text-main)',
          padding: '6px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        <Globe size={14} color="var(--ada-saffron)" aria-hidden="true" />
        <span>Downloads and portal</span>
      </button>

      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        pendingApprovalsCount={pendingApprovalsCount}
        wsConnected={isConnected}
      />

      <main style={{ flex: 1, height: '100vh', overflowY: 'auto', backgroundColor: 'var(--ada-bg-app)' }}>
        {renderContent()}
      </main>
    </div>
  );
};
export default App;
