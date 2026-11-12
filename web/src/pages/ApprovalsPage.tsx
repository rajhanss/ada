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
    <div style={{ flex: 1, height: '100vh', overflowY: 'auto', padding: '32px', backgroundColor: 'var(--ada-bg-app)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <ShieldAlert size={24} color="var(--ada-status-warning)" aria-hidden="true" />
        <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Human-in-the-Loop Authorizations</h2>
      </div>
      <p style={{ fontSize: '13px', color: 'var(--ada-text-secondary)', marginBottom: '24px' }}>
        ADA pauses before taking potentially destructive or critical actions until you review and authorize them.
      </p>

      {approvals.length === 0 ? (
        <div
          style={{
            backgroundColor: 'var(--ada-bg-card)',
            border: '1px solid var(--ada-border-subtle)',
            borderRadius: '10px',
            padding: '32px',
            textAlign: 'center',
            color: 'var(--ada-text-secondary)',
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
                backgroundColor: 'var(--ada-bg-card)',
                border: '1px solid var(--ada-border-focus)',
                borderRadius: '10px',
                padding: '20px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <AlertTriangle size={18} color="var(--ada-status-warning)" aria-hidden="true" />
                <span style={{ fontSize: '15px', fontWeight: 700 }}>Action: {a.tool_name}</span>
                <span
                  style={{
                    backgroundColor: 'var(--ada-saffron-subtle)',
                    color: 'var(--ada-saffron)',
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '4px',
                  }}
                >
                  {a.risk_level} risk
                </span>
              </div>

              <p style={{ fontSize: '13px', color: 'var(--ada-text-main)', marginBottom: '12px' }}>
                {a.reason}
              </p>

              <div
                style={{
                  backgroundColor: 'var(--ada-bg-card-hover)',
                  padding: '10px 14px',
                  borderRadius: '6px',
                  fontFamily: 'var(--ada-font-mono)',
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
                    backgroundColor: 'var(--ada-status-success)',
                    color: 'var(--ada-text-main)',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 18px',
                    fontSize: '13px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'opacity 0.15s ease',
                  }}
                >
                  <Check size={16} aria-hidden="true" /> Approve & Execute
                </button>
                <button
                  onClick={() => handleDecision(a.id, false)}
                  style={{
                    backgroundColor: 'var(--ada-status-danger)',
                    color: 'var(--ada-text-main)',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 18px',
                    fontSize: '13px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'opacity 0.15s ease',
                  }}
                >
                  <X size={16} aria-hidden="true" /> Deny
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
