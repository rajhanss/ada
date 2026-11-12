import React, { useState, useEffect, useRef } from 'react';
import {
  Eye,
  Scan,
  Mic,
  Sparkles,
  ChevronDown,
  Monitor,
  Globe,
  Terminal,
  Shield,
  Send,
  X,
} from 'lucide-react';
import { api } from '../api/client';
import type { AutonomyMode } from '../../../shared/contracts/types';

export type IslandMode = 'compact' | 'expanded' | 'reading_screen' | 'listening' | 'thinking' | 'speaking';

interface DynamicIslandProps {
  onActionTriggered?: (action: string) => void;
  autonomyMode?: AutonomyMode;
  onAutonomyModeChange?: (mode: AutonomyMode) => void;
}

export const DynamicIsland: React.FC<DynamicIslandProps> = ({
  onActionTriggered,
  autonomyMode = 'supervised',
  onAutonomyModeChange,
}) => {
  const [mode, setMode] = useState<IslandMode>('compact');
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isBlinking, setIsBlinking] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  const [statusText, setStatusText] = useState('ADA Online');
  const islandRef = useRef<HTMLDivElement>(null);

  // Mouse pupil tracking
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!islandRef.current) return;
      const rect = islandRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const deltaX = Math.max(-10, Math.min(10, (e.clientX - centerX) / 25));
      const deltaY = Math.max(-6, Math.min(6, (e.clientY - centerY) / 25));
      setMousePos({ x: deltaX, y: deltaY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Periodic natural blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 160);
    }, 3800);
    return () => clearInterval(blinkInterval);
  }, []);

  const triggerScreenAnalysis = async () => {
    setMode('reading_screen');
    setStatusText('Scanning display...');
    try {
      await api.createTask({
        title: 'Screen Element OCR Analysis',
        description: 'Read active window elements',
        tool_name: 'read_screen',
        tool_args: {},
      });
      setTimeout(() => {
        setMode('compact');
        setStatusText('Screen analyzed');
        onActionTriggered?.('Analyzed active screen elements.');
      }, 2200);
    } catch {
      setMode('compact');
    }
  };

  const handleCommandSubmit = async () => {
    if (!commandInput.trim()) return;
    const cmd = commandInput;
    setCommandInput('');
    setMode('thinking');
    setStatusText('Orchestrating plan...');

    try {
      onActionTriggered?.(cmd);
      setTimeout(() => {
        setMode('compact');
        setStatusText('ADA Online');
      }, 1500);
    } catch {
      setMode('compact');
    }
  };

  return (
    <div
      ref={islandRef}
      style={{
        position: 'fixed',
        top: '24px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 9999,
        transition: 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
        width: mode === 'expanded' ? '560px' : mode === 'compact' ? '210px' : '280px',
        minHeight: mode === 'expanded' ? '280px' : '52px',
        backgroundColor: 'rgba(10, 10, 14, 0.88)',
        backdropFilter: 'blur(30px) saturate(190%)',
        WebkitBackdropFilter: 'blur(30px) saturate(190%)',
        borderRadius: mode === 'expanded' ? '28px' : '36px',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        boxShadow: mode === 'expanded'
          ? '0 30px 80px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(232, 117, 24, 0.25)'
          : '0 16px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(232, 117, 24, 0.15)',
        padding: mode === 'expanded' ? '20px 24px' : '8px 16px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        userSelect: 'none',
        overflow: 'hidden',
      }}
    >
      {/* Top Header / Island Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          width: '100%',
        }}
        onClick={() => setMode(mode === 'expanded' ? 'compact' : 'expanded')}
      >
        {/* Animated Cyber-Organic Eyes */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {mode === 'reading_screen' ? (
            /* Scanning Visor */
            <div
              style={{
                width: '42px',
                height: '14px',
                borderRadius: '7px',
                background: 'linear-gradient(90deg, #00C3FF, #E87518)',
                boxShadow: '0 0 12px #00C3FF',
                animation: 'pulse-saffron 1s infinite alternate',
              }}
            />
          ) : (
            /* Expressive Eyes */
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              {/* Left Eye */}
              <div
                style={{
                  width: '16px',
                  height: isBlinking ? '2px' : '16px',
                  borderRadius: '50%',
                  backgroundColor: '#1E1E28',
                  border: '1.5px solid var(--ada-saffron)',
                  boxShadow: '0 0 8px rgba(232, 117, 24, 0.4)',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'height 0.1s ease',
                }}
              >
                {!isBlinking && (
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: '#FFFFFF',
                      boxShadow: '0 0 4px #FFF',
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) translate(${mousePos.x}px, ${mousePos.y}px)`,
                      transition: 'transform 0.05s linear',
                    }}
                  />
                )}
              </div>

              {/* Right Eye */}
              <div
                style={{
                  width: '16px',
                  height: isBlinking ? '2px' : '16px',
                  borderRadius: '50%',
                  backgroundColor: '#1E1E28',
                  border: '1.5px solid var(--ada-saffron)',
                  boxShadow: '0 0 8px rgba(232, 117, 24, 0.4)',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'height 0.1s ease',
                }}
              >
                {!isBlinking && (
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: '#FFFFFF',
                      boxShadow: '0 0 4px #FFF',
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) translate(${mousePos.x}px, ${mousePos.y}px)`,
                      transition: 'transform 0.05s linear',
                    }}
                  />
                )}
              </div>
            </div>
          )}

          <span
            style={{
              fontSize: '12.5px',
              fontWeight: 700,
              letterSpacing: '0.02em',
              color: mode === 'reading_screen' ? '#00C3FF' : '#F3F3F8',
              marginLeft: '4px',
            }}
          >
            {statusText}
          </span>
        </div>

        {/* Compact Right Status Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {mode === 'compact' ? (
            <div
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: 'var(--status-success)',
                boxShadow: '0 0 8px var(--status-success)',
              }}
            />
          ) : (
            <X size={16} color="var(--text-secondary)" />
          )}
        </div>
      </div>

      {/* Expanded Selection Drawer (Apple-style Quick Control Surface) */}
      {mode === 'expanded' && (
        <div style={{ marginTop: '18px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Quick Action Badges */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
            <button
              onClick={triggerScreenAnalysis}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                padding: '12px 6px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(25, 25, 35, 0.6)',
                color: '#FFF',
                cursor: 'pointer',
              }}
            >
              <Scan size={18} color="#00C3FF" />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>See Screen</span>
            </button>

            <button
              onClick={() => onActionTriggered?.('Search web for latest AI news')}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                padding: '12px 6px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(25, 25, 35, 0.6)',
                color: '#FFF',
                cursor: 'pointer',
              }}
            >
              <Globe size={18} color="var(--ada-saffron)" />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>Explore Web</span>
            </button>

            <button
              onClick={() => onActionTriggered?.('Focus window and click start button')}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                padding: '12px 6px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(25, 25, 35, 0.6)',
                color: '#FFF',
                cursor: 'pointer',
              }}
            >
              <Monitor size={18} color="#10B981" />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>Control PC</span>
            </button>

            <button
              onClick={() => onActionTriggered?.('pytest tests/')}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                padding: '12px 6px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(25, 25, 35, 0.6)',
                color: '#FFF',
                cursor: 'pointer',
              }}
            >
              <Terminal size={18} color="#F59E0B" />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>Run Tests</span>
            </button>
          </div>

          {/* Direct Natural Language Command Input */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              backgroundColor: 'rgba(15, 15, 20, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '14px',
              padding: '6px 14px',
            }}
          >
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCommandSubmit()}
              placeholder="Tell ADA what to do or see..."
              style={{
                flex: 1,
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#FFF',
                fontSize: '13px',
              }}
            />
            <button
              onClick={handleCommandSubmit}
              disabled={!commandInput.trim()}
              style={{
                backgroundColor: 'var(--ada-saffron)',
                color: '#FFF',
                border: 'none',
                borderRadius: '8px',
                padding: '6px 12px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Send size={12} /> Run
            </button>
          </div>

          {/* Autonomy Level Footer */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingTop: '6px',
              borderTop: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={14} color="var(--ada-saffron)" />
              <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Target: Windows Primary Workstation
              </span>
            </div>

            <select
              value={autonomyMode}
              onChange={(e) => onAutonomyModeChange?.(e.target.value as AutonomyMode)}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                color: '#FFF',
                border: 'none',
                borderRadius: '6px',
                padding: '3px 8px',
                fontSize: '11px',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              <option value="supervised">Supervised (Standard)</option>
              <option value="bounded">Bounded (Autonomous)</option>
              <option value="assisted">Assisted (Read Only)</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};
