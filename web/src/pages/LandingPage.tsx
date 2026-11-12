import React from 'react';
import {
  Download,
  Laptop,
  Smartphone,
  Globe,
  ShieldCheck,
  Terminal,
  ArrowRight,
  Cpu,
  Layers,
} from 'lucide-react';

interface LandingPageProps {
  onLaunchWebApp: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunchWebApp }) => {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: 'var(--ada-bg-app)',
        color: 'var(--ada-text-main)',
        fontFamily: 'var(--ada-font-sans)',
        overflowX: 'clip',
      }}
    >
      {/* Top Header */}
      <header
        style={{
          borderBottom: '1px solid var(--ada-border-subtle)',
          backgroundColor: 'var(--ada-bg-sidebar)',
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 32px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
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
              fontSize: '14px',
              fontFamily: 'var(--ada-font-mono)',
            }}
          >
            A
          </div>
          <div>
            <span style={{ fontSize: '15px', fontWeight: 700, letterSpacing: '0.01em' }}>
              ADA
            </span>
            <span
              style={{
                fontSize: '11px',
                color: 'var(--ada-text-dim)',
                marginLeft: '8px',
                fontFamily: 'var(--ada-font-mono)',
              }}
            >
              v0.1
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onLaunchWebApp}
          className="ada-btn-primary"
        >
          <span>Launch console</span>
          <ArrowRight size={14} aria-hidden="true" />
        </button>
      </header>

      {/* Main Content Hero */}
      <main style={{ maxWidth: '1120px', margin: '0 auto', padding: '80px 24px 100px' }}>
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <h1
            style={{
              fontSize: 'clamp(36px, 5vw, 54px)',
              fontWeight: 700,
              lineHeight: 1.15,
              letterSpacing: '-0.02em',
              color: 'var(--ada-text-main)',
              marginBottom: '18px',
            }}
          >
            One intelligence across your workstation and phone.
          </h1>

          <p
            style={{
              fontSize: '17px',
              color: 'var(--ada-text-secondary)',
              lineHeight: 1.6,
              maxWidth: '720px',
            }}
          >
            ADA runs as a local daemon on your workstation, understands active display context, executes verified terminal actions, and coordinates authorization requests directly with your mobile device.
          </p>
        </div>

        {/* Distribution Channels */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
            marginBottom: '64px',
          }}
        >
          {/* Windows Desktop */}
          <div className="ada-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--ada-bg-sidebar)',
                  border: '1px solid var(--ada-border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                  color: 'var(--ada-saffron)',
                }}
              >
                <Laptop size={20} aria-hidden="true" />
              </div>

              <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                Windows workstation runtime
              </h2>

              <p style={{ fontSize: '13px', color: 'var(--ada-text-secondary)', lineHeight: 1.6, marginBottom: '24px' }}>
                Native desktop integration with PySide6 floating status orb, screen OCR understanding, background tool execution, and local Python daemon.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <a
                href="/downloads/ada-desktop-setup.exe"
                download="ada-desktop-setup.exe"
                className="ada-btn-primary"
                style={{ width: '100%' }}
              >
                <Download size={15} aria-hidden="true" />
                <span>Download .EXE installer</span>
              </a>
              <span style={{ fontSize: '11px', color: 'var(--ada-text-dim)', textAlign: 'center', fontFamily: 'var(--ada-font-mono)' }}>
                Direct standalone binary (no store gatekeepers)
              </span>
            </div>
          </div>

          {/* Android Companion */}
          <div className="ada-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--ada-bg-sidebar)',
                  border: '1px solid var(--ada-border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                  color: 'var(--ada-status-success)',
                }}
              >
                <Smartphone size={20} aria-hidden="true" />
              </div>

              <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                Android companion client
              </h2>

              <p style={{ fontSize: '13px', color: 'var(--ada-text-secondary)', lineHeight: 1.6, marginBottom: '24px' }}>
                Push-to-talk voice input, live status monitoring of connected workstations, and one-tap cryptographic permission authorizations.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <a
                href="/downloads/ada-mobile.apk"
                download="ada-mobile.apk"
                className="ada-btn-secondary"
                style={{ width: '100%' }}
              >
                <Download size={15} aria-hidden="true" />
                <span>Download .APK package</span>
              </a>
              <span style={{ fontSize: '11px', color: 'var(--ada-text-dim)', textAlign: 'center', fontFamily: 'var(--ada-font-mono)' }}>
                Direct sideload package
              </span>
            </div>
          </div>

          {/* Cloud Web Console */}
          <div className="ada-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--ada-bg-sidebar)',
                  border: '1px solid var(--ada-border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                  color: 'var(--ada-text-main)',
                }}
              >
                <Globe size={20} aria-hidden="true" />
              </div>

              <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                Browser control console
              </h2>

              <p style={{ fontSize: '13px', color: 'var(--ada-text-secondary)', lineHeight: 1.6, marginBottom: '24px' }}>
                Full administrative interface from any browser: inspect active devices, orchestrate tasks, view audit logs, and communicate directly with the agent core.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                type="button"
                onClick={onLaunchWebApp}
                className="ada-btn-secondary"
                style={{ width: '100%' }}
              >
                <span>Launch console</span>
                <ArrowRight size={15} aria-hidden="true" />
              </button>
              <span style={{ fontSize: '11px', color: 'var(--ada-text-dim)', textAlign: 'center', fontFamily: 'var(--ada-font-mono)' }}>
                Zero installation required
              </span>
            </div>
          </div>
        </div>

        {/* Architectural Principles */}
        <div
          style={{
            backgroundColor: 'var(--ada-bg-sidebar)',
            border: '1px solid var(--ada-border-subtle)',
            borderRadius: '8px',
            padding: '32px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <ShieldCheck size={20} color="var(--ada-saffron)" aria-hidden="true" />
            <h3 style={{ fontSize: '16px', fontWeight: 600 }}>
              Autonomous execution and security architecture
            </h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--ada-text-secondary)', lineHeight: 1.65 }}>
            Operating-system level computer use requires capabilities that sandboxed web containers cannot provide: active display inspection, hotkey handling, and local process management. By combining direct desktop packages with hardware-bound authorization gates, ADA executes commands while keeping you in full supervisory control.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--ada-border-subtle)',
          backgroundColor: 'var(--ada-bg-sidebar)',
          padding: '24px',
          textAlign: 'center',
          fontSize: '12px',
          color: 'var(--ada-text-dim)',
          fontFamily: 'var(--ada-font-mono)',
        }}
      >
        ADA Autonomous Digital Assistant: security-first workstation and mobile intelligence.
      </footer>
    </div>
  );
};
