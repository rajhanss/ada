import React, { useState, useEffect } from 'react';
import { ListTodo, CheckCircle2, Clock, XCircle, Play } from 'lucide-react';
import { api } from '../api/client';
import type { Task } from '../../../shared/contracts/types';

export const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [, setLoading] = useState(true);

  useEffect(() => {
    api.listTasks()
      .then(setTasks)
      .catch(() => {
        // Fallback demo tasks
        setTasks([
          {
            id: 'task-001',
            user_id: 'user',
            title: 'Run test suite on backend',
            description: 'Run pytest tests/ on Windows workstation',
            tool_name: 'run_dev_command',
            tool_args: { command: 'pytest tests/ -v' },
            priority: 5,
            status: 'completed',
            result: { passed: 73, failed: 0 },
            created_at: new Date(Date.now() - 3600000).toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'task-002',
            user_id: 'user',
            title: 'Screen Element OCR Analysis',
            description: 'Analyze active window layout and buttons',
            tool_name: 'read_screen',
            tool_args: {},
            priority: 3,
            status: 'completed',
            result: { detected_elements: 14 },
            created_at: new Date(Date.now() - 1800000).toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 size={16} color="var(--ada-status-success)" aria-label="Completed" />;
      case 'running':
        return <Play size={16} color="var(--ada-saffron)" aria-label="Running" />;
      case 'failed':
        return <XCircle size={16} color="var(--ada-status-danger)" aria-label="Failed" />;
      default:
        return <Clock size={16} color="var(--ada-status-warning)" aria-label="Pending" />;
    }
  };

  return (
    <div style={{ flex: 1, height: '100vh', overflowY: 'auto', padding: '32px', backgroundColor: 'var(--ada-bg-app)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <ListTodo size={24} color="var(--ada-saffron)" aria-hidden="true" />
        <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Autonomous Task Monitor</h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {tasks.map((t) => (
          <div
            key={t.id}
            style={{
              backgroundColor: 'var(--ada-bg-card)',
              border: '1px solid var(--ada-border-subtle)',
              borderRadius: '8px',
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                <span style={{ fontSize: '14px', fontWeight: 600 }}>{t.title}</span>
                <span
                  style={{
                    fontSize: '11px',
                    fontFamily: 'var(--ada-font-mono)',
                    backgroundColor: 'var(--ada-bg-card-hover)',
                    border: '1px solid var(--ada-border-subtle)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    color: 'var(--ada-saffron)',
                  }}
                >
                  {t.tool_name}
                </span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--ada-text-secondary)' }}>{t.description}</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {getStatusIcon(t.status)}
              <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'capitalize' }}>
                {t.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
