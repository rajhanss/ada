import React from 'react';
import {
  Download,
  Laptop,
  Smartphone,
  Globe,
  Sparkles,
  ShieldCheck,
  Zap,
  Eye,
  CheckCircle2,
  Terminal,
  ArrowRight,
} from 'lucide-react';
import { DynamicIsland } from '../components/DynamicIsland';

interface LandingPageProps {
  onLaunchWebApp: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunchWebApp }) => {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#070709',
        color: '#F3F3F8',
        fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
        overflowX: 'hidden',
        position: 'relative',
      }}
    >
      {/* Live Interactive Dynamic Island Floating at the top */}
      <DynamicIsland />

      {/* Hero Section */}
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '120px 24px 60px',
          textAlign: 'center',
          position: 'relative',
        }}
      >
        {/* Glow backdrop */}
        <div
          style={{
            position: 'absolute',
            top: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '600px',
            height: '350px',
            background: 'radial-gradient(circle, rgba(232, 117, 24, 0.15) 0%, rgba(0,0,0,0) 70%)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        {/* Hero Tag */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'rgba(232, 117, 24, 0.12)',
            border: '1px solid rgba(232, 117, 24, 0.3)',
            borderRadius: '999px',
            padding: '6px 16px',
            fontSize: '12px',
            fontWeight: 700,
            color: 'var(--ada-saffron)',
            marginBottom: '24px',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <Sparkles size={14} /> ONE INTELLIGENCE. EVERY DEVICE. INDEPENDENT ACTION.
        </div>

        {/* Hero Headline */}
        <h1
          style={{
            fontSize: 'clamp(40px, 6vw, 68px)',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            marginBottom: '20px',
            position: 'relative',
            zIndex: 1,
          }}
        >
          Your computer, controlled by <br />
          <span
            style={{
              background: 'linear-gradient(135deg, #FFF 30%, #E87518 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Autonomous Digital Intelligence.
          </span>
        </h1>

        <p
          style={{
            fontSize: '18px',
            color: '#9B9BAF',
            maxWidth: '680px',
            margin: '0 auto 40px',
            lineHeight: 1.6,
            position: 'relative',
            zIndex: 1,
          }}
        >
          ADA lives by your cursor, sees what you see, explores the web, executes commands on your workstation, and stays synchronized with your phone.
        </p>

        {/* Primary Download & Web Action Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '20px',
            maxWidth: '960px',
            margin: '0 auto 80px',
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Windows Download Card */}
          <div
            style={{
              backgroundColor: '#121217',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '32px 24px',
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
              transition: 'transform 0.2s ease, border-color 0.2s ease',
            }}
          >
            <div>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(232, 117, 24, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <Laptop size={22} color="var(--ada-saffron)" />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px' }}>
                Download for Windows
              </h3>
              <p style={{ fontSize: '13px', color: '#8E8E9F', marginBottom: '20px', lineHeight: 1.5 }}>
                Full workstation control: screen understanding, PySide6 dynamic floating orb, mouse/keyboard automation, and local execution.
              </p>
            </div>

            <a
              href="/downloads/ada-desktop-setup.exe"
              download="ada-desktop-setup.exe"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                backgroundColor: 'var(--ada-saffron)',
                color: '#FFF',
                padding: '12px 20px',
                borderRadius: '12px',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '14px',
                boxShadow: '0 8px 24px rgba(232, 117, 24, 0.35)',
              }}
            >
              <Download size={16} /> Download .EXE (Direct)
            </a>
          </div>

          {/* Android Download Card */}
          <div
            style={{
              backgroundColor: '#121217',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '32px 24px',
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
            }}
          >
            <div>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(0, 195, 255, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <Smartphone size={22} color="#00C3FF" />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px' }}>
                Download for Android
              </h3>
              <p style={{ fontSize: '13px', color: '#8E8E9F', marginBottom: '20px', lineHeight: 1.5 }}>
                Direct APK sideload without Play Store gatekeepers. Push-to-talk voice commands, live laptop monitoring, and 1-tap push approvals.
              </p>
            </div>

            <a
              href="/downloads/ada-mobile.apk"
              download="ada-mobile.apk"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                backgroundColor: '#1E1E28',
                color: '#FFF',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                padding: '12px 20px',
                borderRadius: '12px',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '14px',
              }}
            >
              <Download size={16} /> Download .APK (Direct)
            </a>
          </div>

          {/* Web App Card */}
          <div
            style={{
              backgroundColor: '#121217',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '32px 24px',
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
            }}
          >
            <div>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <Globe size={22} color="#10B981" />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px' }}>
                Cloud Web Dashboard
              </h3>
              <p style={{ fontSize: '13px', color: '#8E8E9F', marginBottom: '20px', lineHeight: 1.5 }}>
                No installation needed. Manage connected devices, orchestrate tasks, inspect persistent memory, and chat directly from any browser.
              </p>
            </div>

            <button
              onClick={onLaunchWebApp}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                backgroundColor: '#10B981',
                color: '#FFF',
                border: 'none',
                padding: '12px 20px',
                borderRadius: '12px',
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: '14px',
                boxShadow: '0 8px 24px rgba(16, 185, 129, 0.35)',
              }}
            >
              Launch Web App <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* Store-Free Distribution Architectural Callout */}
        <div
          style={{
            maxWidth: '960px',
            margin: '0 auto',
            backgroundColor: 'rgba(18, 18, 24, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '28px 32px',
            textAlign: 'left',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <ShieldCheck size={20} color="var(--ada-saffron)" />
            <h4 style={{ fontSize: '16px', fontWeight: 700 }}>
              Why Standalone Distribution Without App Stores?
            </h4>
          </div>
          <p style={{ fontSize: '13.5px', color: '#9B9BAF', lineHeight: 1.6 }}>
            True autonomous computer use requires permissions that closed app stores prohibit: direct screen reading, global keyboard hotkeys, background dev tool execution, and local shell control. By distributing direct signed <strong>.EXE</strong> packages on Windows and sideloadable <strong>.APK</strong> bundles on Android, ADA operates with full native performance and zero app store surveillance or restrictions.
          </p>
        </div>
      </div>
    </div>
  );
};
