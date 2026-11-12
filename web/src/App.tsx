import React, { useState } from 'react';
import { Sidebar, type TabType } from './components/Sidebar';
import { ChatPage } from './pages/ChatPage';
import { TasksPage } from './pages/TasksPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { DevicesPage } from './pages/DevicesPage';
import { useAdaWebSocket } from './hooks/useAdaWebSocket';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<TabType>('chat');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState(1);
  const { isConnected } = useAdaWebSocket();

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
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
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
