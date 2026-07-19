'use client';

import { useState, useRef, useEffect } from 'react';
import { Bot, Send, RotateCcw, Target, Clock, Zap, Copy, Check } from 'lucide-react';
import { api } from '@/services/api';
import type { MentorMessage } from '@/types';

const SUGGESTED_ACTIONS = [
  { label: 'Explain Today\'s Lesson', prompt: "Can you explain HTTP Authentication in detail? I want to understand Basic Auth, Digest Auth, and JWTs." },
  { label: 'Quiz Me', prompt: "Quiz me on what I should know before starting HTTP Authentication." },
  { label: 'Review My Resume', prompt: "Based on my profile, what are the biggest gaps in my resume for a Penetration Tester role?" },
  { label: 'Help With My Project', prompt: "I'm building a Web Vulnerability Scanner in Python. What should I prioritize implementing first?" },
  { label: 'Explain My Roadmap', prompt: "Why is HTTP Authentication placed before Burp Suite in my roadmap?" },
  { label: 'Career Advice', prompt: "What's the fastest path from my current skill level to landing a junior pentesting job?" },
];



function MessageBubble({ message }: { message: MentorMessage }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple markdown renderer
  const renderContent = (text: string) => {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 rounded bg-white/[0.08] text-blue-300 text-xs font-mono">$1</code>')
      .split('\n')
      .map((line, i) => {
        if (line.match(/^\d+\.\s/)) {
          return `<div class="flex gap-2 my-1"><span class="text-zinc-500 font-mono text-xs mt-0.5">${line.match(/^(\d+)\./)?.[1]}.</span><span>${line.replace(/^\d+\.\s/, '')}</span></div>`;
        }
        if (line.startsWith('**') && line.endsWith('**')) {
          return `<div class="font-semibold text-[#fafafa] mt-3 mb-1">${line.slice(2, -2)}</div>`;
        }
        if (line === '') return '<div class="h-2"></div>';
        return `<p class="leading-relaxed">${line}</p>`;
      })
      .join('');
  };

  return (
    <div className={`flex gap-3 group ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot className="w-4 h-4 text-blue-400" />
        </div>
      )}
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-blue-500 text-white rounded-br-sm'
              : 'bg-[#18181b] border border-white/[0.06] text-zinc-300 rounded-bl-sm'
          }`}
          dangerouslySetInnerHTML={isUser ? undefined : { __html: renderContent(message.content) }}
        >
          {isUser ? message.content : null}
        </div>
        {!isUser && (
          <div className="flex items-center gap-2 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={copy} className="flex items-center gap-1 text-xs text-zinc-600 hover:text-zinc-400 transition-colors">
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function MentorPage() {
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const d = await api.getDashboardData();
        setData(d.data);
      } catch (e) {
        console.error(e);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (!data) return <div className="p-8 text-white animate-pulse">Loading mentor...</div>;
  const { profile, mentorContext } = data;

  const send = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    const userMsg: MentorMessage = { id: Date.now().toString(), role: 'user', content: msg, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.chat(msg);
      if (res.success && res.response) {
        const aiMsg: MentorMessage = {
          id: (Date.now() + 1).toString(), role: 'assistant',
          content: res.response,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMsg]);
      } else {
        throw new Error('No response');
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(), role: 'assistant',
        content: 'I am sorry, but I am currently unavailable. Please try again later.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setMessages([]);
    setInput('');
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-3.5rem-3rem)] flex flex-col animate-fade-in">

      {/* ── Context Card ──────────────────────────────────────────────────── */}
      <div className="surface p-4 mb-4 flex-shrink-0">
        <div className="flex items-start gap-4 flex-wrap">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm text-[#fafafa]">Your AI Mentor</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs text-zinc-500">Online</span>
              </div>
              <div className="text-xs text-zinc-400 mt-0.5">
                Knows your profile, your roadmap, and your progress
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs text-zinc-500">
              <Target className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-[#fafafa] font-medium">{profile?.readiness || 0}%</span> ready
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-500">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[#fafafa] font-medium">{profile?.currentStreak || 0}</span> day streak
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-500">
              <Clock className="w-3.5 h-3.5 text-zinc-500" />
              <span className="text-[#fafafa] font-medium">{mentorContext?.estimatedTimeToReady || 'Unknown'}</span> to ready
            </div>
          </div>
        </div>
      </div>

      {/* ── Chat Area ─────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto space-y-5 pb-4">
        {messages.map(m => <MessageBubble key={m.id} message={m} />)}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-blue-400" />
            </div>
            <div className="bg-[#18181b] border border-white/[0.06] rounded-xl rounded-bl-sm px-4 py-3 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Suggested Actions ─────────────────────────────────────────────── */}
      {messages.length <= 1 && !loading && (
        <div className="flex flex-wrap gap-2 mb-3 flex-shrink-0">
          {SUGGESTED_ACTIONS.map(a => (
            <button
              key={a.label}
              onClick={() => send(a.prompt)}
              className="px-3 py-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] text-xs text-zinc-400 hover:text-[#fafafa] hover:border-white/[0.12] hover:bg-white/[0.06] transition-all"
            >
              {a.label}
            </button>
          ))}
        </div>
      )}

      {/* ── Input ─────────────────────────────────────────────────────────── */}
      <div className="flex-shrink-0 surface p-3 flex items-end gap-3">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
          placeholder="Ask your mentor anything..."
          rows={1}
          className="flex-1 bg-transparent text-sm text-[#fafafa] placeholder-zinc-600 resize-none focus:outline-none max-h-32 leading-relaxed py-1"
          style={{ height: 'auto' }}
          onInput={e => {
            const t = e.target as HTMLTextAreaElement;
            t.style.height = 'auto';
            t.style.height = Math.min(t.scrollHeight, 128) + 'px';
          }}
        />
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={reset}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-zinc-600 hover:text-zinc-400 hover:bg-white/[0.06] transition-colors"
            title="Clear chat"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => send()}
            disabled={!input.trim() || loading}
            className="w-8 h-8 rounded-lg bg-blue-500 hover:bg-blue-600 disabled:bg-zinc-800 disabled:text-zinc-600 flex items-center justify-center text-white transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
