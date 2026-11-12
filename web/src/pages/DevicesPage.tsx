import React, { useState, useEffect } from 'react';
import { Laptop, Smartphone, Globe, Plus, QrCode } from 'lucide-react';
import { api } from '../api/client';
import type { Device } from '../../../shared/contracts/types';

export const DevicesPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);

  useEffect(() => {
    api.listDevices()
      .then(setDevices)
      .catch(() => {
        // Fallback demo devices
        setDevices([
          {
            id: 'dev-win-01',
            user_id: 'user',
            device_type: 'desktop',
            display_name: 'Windows Primary Workstation',
            platform: 'windows',
            capabilities: ['screen_reading', 'shell_execution', 'file_io', 'ui_automation'],
            is_online: true,
            created_at: new Date(Date.now() - 86400000).toISOString(),
          },
          {
            id: 'dev-mob-01',
            user_id: 'user',
            device_type: 'mobile',
            display_name: 'Pixel Mobile Companion',
            platform: 'android',
            capabilities: ['voice_input', 'remote_dispatch', 'push_notifications'],
            is_online: true,
            created_at: new Date(Date.now() - 43200000).toISOString(),
          },
        ]);
      });
  }, []);

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'desktop':
        return <Laptop size={20} color="var(--ada-saffron)" />;
      case 'mobile':
        return <Smartphone size={20} color="#00C3FF" />;
      default:
        return <Globe size={20} color="#8CE650" />;
    }
  };

  return (
    <div style={{ flex: 1, height: '100vh', overflowY: 'auto', padding: '32px', backgroundColor: 'var(--bg-app)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Registered Workstations & Companions</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            One intelligence operating synchronously across all your endpoints.
          </p>
        </div>

        <button
          style={{
            backgroundColor: 'var(--ada-saffron)',
            color: '#FFF',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <QrCode size={16} /> Pair New Device
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
        {devices.map((d) => (
          <div
            key={d.id}
            style={{
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {getDeviceIcon(d.device_type)}
                <span style={{ fontSize: '15px', fontWeight: 700 }}>{d.display_name}</span>
              </div>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '11px',
                  color: 'var(--status-success)',
                  fontWeight: 600,
                }}
              >
                <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--status-success)' }} />
                Online
              </span>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Platform: <span style={{ textTransform: 'capitalize', color: 'var(--text-main)' }}>{d.platform}</span>
            </p>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                Permitted Capabilities
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                {d.capabilities.map((c) => (
                  <span
                    key={c}
                    style={{
                      fontSize: '11px',
                      fontFamily: 'var(--font-mono)',
                      backgroundColor: 'var(--bg-card-hover)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
