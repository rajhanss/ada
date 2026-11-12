import React, { useState, useEffect, useRef } from 'react';
import { Send, Laptop, Shield, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';
import type { Message, AutonomyMode } from '../../../shared/contracts/types';

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [autonomyMode, setAutonomyMode] = useState<AutonomyMode>('supervised');
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<string>('default_active_session');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize or load conversation
    api.listConversations()
      .then((convs) => {
        if (convs.length > 0) {
          setConversationId(convs[0].id);
          api.getMessages(convs[0].id).then(setMessages);
        } else {
          api.createConversation('Workstation Control Session').then((c) => {
            setConversationId(c.id);
            setMessages([
              {
                id: 'welcome',
                conversation_id: c.id,
                user_id: 'ada',
                role: 'assistant',
                content: 'Hello! I am ADA, your persistent personal assistant. I am linked to your Windows computer, mobile companion, and cloud backend.',
                content_type: 'text',
                created_at: new Date().toISOString(),
              },
            ]);
          });
        }
      })
      .catch(() => {
        // Fallback demo state
        setMessages([
          {
            id: 'demo-welcome',
            conversation_id: 'demo',
            user_id: 'ada',
            role: 'assistant',
            content: 'ADA Cloud Intelligence Core is ready. What would you like to inspect or execute?',
            content_type: 'text',
            created_at: new Date().toISOString(),
          },
        ]);
      });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isSending) return;

    setInputText('');
    setIsSending(true);

    // Optimistic user message
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId,
      user_id: 'user',
      role: 'user',
      content: text,
      content_type: 'text',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const responseMsg = await api.sendMessage(conversationId, text, autonomyMode);
      setMessages((prev) => [...prev, responseMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          conversation_id: conversationId,
          user_id: 'ada',
          role: 'assistant',
          content: `⚠️ Failed to execute: ${err.message}`,
          content_type: 'text',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div style={{ flex: 1, height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-app)' }}>
      {/* Top Bar */}
      <header
        style={{
          height: '60px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          backgroundColor: 'var(--bg-sidebar)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Laptop size={16} color="var(--ada-saffron)" />
            <span style={{ fontSize: '13px', fontWeight: 600 }}>Windows Primary Workstation</span>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--status-success)' }} />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Shield size={16} color="var(--text-secondary)" />
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Autonomy Policy:</span>
          <select
            value={autonomyMode}
            onChange={(e) => setAutonomyMode(e.target.value as AutonomyMode)}
            style={{
              backgroundColor: 'var(--bg-card)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="supervised">Supervised (Standard)</option>
            <option value="bounded">Bounded (Pre-approved scripts)</option>
            <option value="assisted">Assisted (Read-only)</option>
            <option value="conversation">Conversation Only</option>
          </select>
        </div>
      </header>

      {/* Message Feed */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              style={{
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: '75%',
                backgroundColor: isUser ? '#23232C' : 'var(--bg-card)',
                border: `1px solid ${isUser ? '#363644' : 'var(--border-subtle)'}`,
                borderRadius: '12px',
                padding: '14px 18px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: isUser ? '#A0A0B8' : 'var(--ada-saffron)' }}>
                  {isUser ? 'You' : 'ADA'}
                </span>
                {m.metadata?.requires_approval && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: 'var(--status-warning)', fontWeight: 600 }}>
                    <AlertTriangle size={12} /> Awaiting Approval
                  </span>
                )}
              </div>
              <div style={{ fontSize: '13.5px', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
                {m.content}
              </div>
            </div>
          );
        })}
        {isSending && (
          <div style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '12px' }}>
            <Sparkles size={16} className="orb-pulse" color="var(--ada-saffron)" />
            <span>ADA is contextualizing and orchestrating...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <footer style={{ padding: '16px 24px', backgroundColor: 'var(--bg-sidebar)', borderTop: '1px solid var(--border-subtle)' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '8px 14px',
          }}
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Direct ADA: 'Inspect recent changes on desktop and run the test suite'..."
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-main)',
              fontSize: '14px',
            }}
          />
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || isSending}
            style={{
              backgroundColor: inputText.trim() ? 'var(--ada-saffron)' : 'var(--border-subtle)',
              color: '#FFF',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              fontWeight: 600,
              fontSize: '13px',
              cursor: inputText.trim() ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Send size={14} /> Send
          </button>
        </div>
      </footer>
    </div>
  );
};
