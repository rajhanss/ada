import React, { useState } from 'react';
import { Sidebar, type TabType } from './components/Sidebar';
import { ChatPage } from './pages/ChatPage';
import { TasksPage } from './pages/TasksPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { DevicesPage } from './pages/DevicesPage';
import { LandingPage } from './pages/LandingPage';
import { DynamicIsland } from './components/DynamicIsland';
import { useAdaWebSocket } from './hooks/useAdaWebSocket';
import { Sparkles, LayoutDashboard, Globe } from 'lucide-react';

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
            <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '12px' }}>
              Persistent Memory & Episodic Retrieval
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
              Inspect long-term user preferences, project knowledge, and verified workflows learned by ADA.
            </p>
          </div>
        );
      default:
        return <ChatPage />;
    }
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden', position: 'relative' }}>
      {/* Floating Apple-Style Dynamic Island inside workspace as well */}
      <DynamicIsland onActionTriggered={(action) => console.log('Action triggered from Island:', action)} />

      {/* View Switcher Top-Right Pill */}
      <button
        onClick={() => setView('landing')}
        style={{
          position: 'fixed',
          top: '16px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: 'rgba(25, 25, 35, 0.85)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: '#FFF',
          padding: '6px 14px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        <Globe size={14} color="var(--ada-saffron)" /> SaaS Website & Downloads
      </button>

      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        pendingApprovalsCount={pendingApprovalsCount}
        wsConnected={isConnected}
      />
      <main style={{ flex: 1, height: '100vh', display: 'flex' }}>
        {renderContent()}
      </main>
    </div>
  );
};
