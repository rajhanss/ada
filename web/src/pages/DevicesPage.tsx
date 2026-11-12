import React, { useState, useEffect } from 'react';
import { Laptop, Smartphone, Globe, QrCode } from 'lucide-react';
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
        return <Laptop size={20} color="var(--ada-saffron)" aria-label="Desktop Workstation" />;
      case 'mobile':
        return <Smartphone size={20} color="var(--ada-text-main)" aria-label="Mobile Companion" />;
      default:
        return <Globe size={20} color="var(--ada-status-success)" aria-label="Network Node" />;
    }
  };

  return (
    <div style={{ flex: 1, height: '100vh', overflowY: 'auto', padding: '32px', backgroundColor: 'var(--ada-bg-app)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Registered Workstations & Companions</h2>
          <p style={{ fontSize: '13px', color: 'var(--ada-text-secondary)' }}>
            One intelligence operating synchronously across all your endpoints.
          </p>
        </div>

        <button
          style={{
            backgroundColor: 'var(--ada-saffron)',
            color: 'var(--ada-text-main)',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background-color 0.15s ease',
          }}
        >
          <QrCode size={16} aria-hidden="true" /> Pair New Device
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
        {devices.map((d) => (
          <div
            key={d.id}
            style={{
              backgroundColor: 'var(--ada-bg-card)',
              border: '1px solid var(--ada-border-subtle)',
              borderRadius: '8px',
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
                  color: 'var(--ada-status-success)',
                  fontWeight: 600,
                }}
              >
                <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--ada-status-success)' }} />
                Online
              </span>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--ada-text-secondary)', marginBottom: '16px' }}>
              Platform: <span style={{ textTransform: 'capitalize', color: 'var(--ada-text-main)' }}>{d.platform}</span>
            </p>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--ada-text-dim)', fontWeight: 600 }}>
                Permitted capabilities
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                {d.capabilities.map((c) => (
                  <span
                    key={c}
                    style={{
                      fontSize: '11px',
                      fontFamily: 'var(--ada-font-mono)',
                      backgroundColor: 'var(--ada-bg-card-hover)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      color: 'var(--ada-text-secondary)',
                      border: '1px solid var(--ada-border-subtle)',
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
