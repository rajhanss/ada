import React, { useState, useEffect, useRef } from 'react';
import {
  Eye,
  Scan,
  Mic,
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
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 9999,
        transition: 'opacity 0.2s ease, transform 0.2s ease',
        width: mode === 'expanded' ? '540px' : mode === 'compact' ? '210px' : '280px',
        minHeight: mode === 'expanded' ? '260px' : '48px',
        backgroundColor: 'var(--ada-bg-sidebar)',
        borderRadius: mode === 'expanded' ? '12px' : '24px',
        border: '1px solid var(--ada-border-strong)',
        padding: mode === 'expanded' ? '20px' : '8px 16px',
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
        {/* Assistant Status & Eye indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {mode === 'reading_screen' ? (
            <div
              style={{
                width: '36px',
                height: '12px',
                borderRadius: '6px',
                backgroundColor: 'var(--ada-saffron)',
              }}
            />
          ) : (
            <div style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
              <div
                style={{
                  width: '14px',
                  height: isBlinking ? '2px' : '14px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--ada-bg-app)',
                  border: '1.5px solid var(--ada-saffron)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {!isBlinking && (
                  <div
                    style={{
                      width: '5px',
                      height: '5px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--ada-text-main)',
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) translate(${mousePos.x}px, ${mousePos.y}px)`,
                    }}
                  />
                )}
              </div>

              <div
                style={{
                  width: '14px',
                  height: isBlinking ? '2px' : '14px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--ada-bg-app)',
                  border: '1.5px solid var(--ada-saffron)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {!isBlinking && (
                  <div
                    style={{
                      width: '5px',
                      height: '5px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--ada-text-main)',
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) translate(${mousePos.x}px, ${mousePos.y}px)`,
                    }}
                  />
                )}
              </div>
            </div>
          )}

          <span
            style={{
              fontSize: '12px',
              fontWeight: 600,
              color: mode === 'reading_screen' ? 'var(--ada-saffron)' : 'var(--ada-text-main)',
              marginLeft: '4px',
              fontFamily: 'var(--ada-font-mono)',
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
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: 'var(--ada-status-success)',
              }}
            />
          ) : (
            <X size={15} color="var(--ada-text-secondary)" aria-hidden="true" />
          )}
        </div>
      </div>

      {/* Expanded Quick Actions Panel */}
      {mode === 'expanded' && (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Quick command input */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCommandSubmit()}
              placeholder="Tell ADA what to execute..."
              style={{
                flex: 1,
                backgroundColor: 'var(--ada-bg-app)',
                border: '1px solid var(--ada-border-subtle)',
                borderRadius: '6px',
                padding: '8px 12px',
                color: 'var(--ada-text-main)',
                fontSize: '13px',
                fontFamily: 'var(--ada-font-sans)',
                outline: 'none',
              }}
            />
            <button
              type="button"
              onClick={handleCommandSubmit}
              className="ada-btn-primary"
              style={{ padding: '8px 14px' }}
            >
              <Send size={14} aria-hidden="true" />
            </button>
          </div>

          {/* Action triggers */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={triggerScreenAnalysis}
              className="ada-btn-secondary"
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              <Scan size={13} aria-hidden="true" />
              <span>Analyze active screen</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setMode('listening');
                setStatusText('Listening for voice...');
                setTimeout(() => {
                  setMode('compact');
                  setStatusText('ADA Online');
                }, 3000);
              }}
              className="ada-btn-secondary"
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              <Mic size={13} aria-hidden="true" />
              <span>Voice input</span>
            </button>
          </div>

          {/* Autonomy mode selector */}
          <div
            style={{
              paddingTop: '12px',
              borderTop: '1px solid var(--ada-border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '11px',
              color: 'var(--ada-text-secondary)',
            }}
          >
            <span>Autonomy policy:</span>
            <div style={{ display: 'flex', gap: '4px' }}>
              {(['supervised', 'semi_autonomous', 'full_autonomous'] as AutonomyMode[]).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => onAutonomyModeChange?.(m)}
                  style={{
                    backgroundColor: autonomyMode === m ? 'var(--ada-saffron)' : 'var(--ada-bg-card)',
                    color: 'var(--ada-text-main)',
                    border: '1px solid var(--ada-border-subtle)',
                    borderRadius: '4px',
                    padding: '2px 8px',
                    fontSize: '10px',
                    fontFamily: 'var(--ada-font-mono)',
                    cursor: 'pointer',
                  }}
                >
                  {m.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
