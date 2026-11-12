import React, { useState, useEffect } from 'react';
import { ShieldAlert, Check, X, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';
import type { ApprovalRequest } from '../../../shared/contracts/types';

interface ApprovalsPageProps {
  onApprovalResolved?: () => void;
}

export const ApprovalsPage: React.FC<ApprovalsPageProps> = ({ onApprovalResolved }) => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);

  useEffect(() => {
    api.listApprovals()
      .then(setApprovals)
      .catch(() => {
        // Fallback demo approval item
        setApprovals([
          {
            id: 'appr-101',
            user_id: 'user',
            tool_name: 'delete_file',
            tool_args: { path: 'C:\\Projects\\cache\\temp_build.bin' },
            risk_level: 'high',
            reason: "'delete_file' always requires explicit user approval before removal.",
            status: 'pending',
            created_at: new Date().toISOString(),
          },
        ]);
      });
  }, []);

  const handleDecision = async (id: string, approved: boolean) => {
    try {
      await api.resolveApproval(id, approved);
    } catch {}
    setApprovals((prev) => prev.filter((a) => a.id !== id));
    onApprovalResolved?.();
  };

  return (
    <div style={{ flex: 1, height: '100vh', overflowY: 'auto', padding: '32px', backgroundColor: 'var(--bg-app)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <ShieldAlert size={24} color="var(--status-warning)" />
        <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Human-in-the-Loop Authorizations</h2>
      </div>
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
        ADA pauses before taking potentially destructive or critical actions until you review and authorize them.
      </p>

      {approvals.length === 0 ? (
        <div
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '32px',
            textAlign: 'center',
            color: 'var(--text-secondary)',
          }}
        >
          No pending authorizations. ADA is operating within permitted autonomy boundaries.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {approvals.map((a) => (
            <div
              key={a.id}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid #E87518',
                borderRadius: '10px',
                padding: '20px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <AlertTriangle size={18} color="var(--status-warning)" />
                <span style={{ fontSize: '15px', fontWeight: 700 }}>Action: {a.tool_name}</span>
                <span
                  style={{
                    backgroundColor: 'rgba(232, 117, 24, 0.2)',
                    color: 'var(--ada-saffron)',
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    textTransform: 'uppercase',
                  }}
                >
                  {a.risk_level} Risk
                </span>
              </div>

              <p style={{ fontSize: '13px', color: 'var(--text-main)', marginBottom: '12px' }}>
                {a.reason}
              </p>

              <div
                style={{
                  backgroundColor: 'var(--bg-card-hover)',
                  padding: '10px 14px',
                  borderRadius: '6px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  marginBottom: '16px',
                }}
              >
                Arguments: {JSON.stringify(a.tool_args, null, 2)}
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={() => handleDecision(a.id, true)}
                  style={{
                    backgroundColor: 'var(--status-success)',
                    color: '#FFF',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 18px',
                    fontSize: '13px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <Check size={16} /> Approve & Execute
                </button>
                <button
                  onClick={() => handleDecision(a.id, false)}
                  style={{
                    backgroundColor: 'var(--status-danger)',
                    color: '#FFF',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 18px',
                    fontSize: '13px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <X size={16} /> Deny
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
