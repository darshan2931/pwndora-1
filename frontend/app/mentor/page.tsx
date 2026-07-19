'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { MENTOR_SUGGESTED_QUESTIONS } from '@/constants';
import { MentorMessage } from '@/types';
import { useToast } from '@/components/ui';
import { useAuth } from '@/components/AuthContext';
import { mentorChat, clearMentorSession, getAssessment } from '@/services/api';
import Link from 'next/link';

const TOPIC_CATEGORIES = [
  { label: 'Career Advice', icon: '🎯', questions: ['How do I break into cybersecurity?', 'What cybersecurity role suits me best?', 'How do I transition from IT to security?'] },
  { label: 'Certifications', icon: '📜', questions: ['What certifications should I get first?', 'Is OSCP worth it for beginners?', 'CompTIA Security+ vs CySA+, which should I get?'] },
  { label: 'Skills & Learning', icon: '🧠', questions: ['What are the most in-demand security skills?', 'How long does it take to learn penetration testing?', 'Should I learn Python or Bash first?'] },
  { label: 'Projects & Portfolio', icon: '💼', questions: ['What projects should I build for my portfolio?', 'How do I make my GitHub stand out to employers?', 'What are good home lab setups?'] },
];

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-xs font-mono">$1</code>');

  const lines = html.split('\n');
  let result = '';
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();

    if (/^\d+\.\s/.test(trimmed)) {
      if (!inList) { result += '<ol class="list-decimal list-inside space-y-1 my-2">'; inList = true; }
      result += `<li class="text-sm">${trimmed.replace(/^\d+\.\s/, '')}</li>`;
    } else if (trimmed.startsWith('- ')) {
      if (!inList) { result += '<ul class="list-disc list-inside space-y-1 my-2">'; inList = true; }
      result += `<li class="text-sm">${trimmed.slice(2)}</li>`;
    } else {
      if (inList) { result += inList ? '</ul>' : ''; inList = false; }
      if (trimmed === '') {
        result += '<br/>';
      } else {
        result += `<p class="text-sm my-1">${trimmed}</p>`;
      }
    }
  }
  if (inList) result += '</ul>';

  return result;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      title="Copy message"
    >
      {copied ? (
        <svg className="w-3.5 h-3.5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      ) : (
        <svg className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75" />
        </svg>
      )}
    </button>
  );
}

function FollowUpSuggestions({ suggestions, onSelect }: { suggestions: string[]; onSelect: (q: string) => void }) {
  if (suggestions.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1.5 mt-2 ml-10">
      {suggestions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="text-xs px-2.5 py-1.5 rounded-full border border-primary/30 dark:border-primary/40 text-primary dark:text-primary hover:bg-primary/5 dark:hover:bg-primary/10 transition-all"
        >
          {q}
        </button>
      ))}
    </div>
  );
}

function TopicCategories({ onSelect }: { onSelect: (q: string) => void }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto mb-6">
      {TOPIC_CATEGORIES.map((cat) => (
        <div key={cat.label}>
          <button
            onClick={() => setExpanded(expanded === cat.label ? null : cat.label)}
            className={`w-full text-left p-3 rounded-xl border transition-all ${
              expanded === cat.label
                ? 'border-primary/40 bg-primary/5 dark:bg-primary/10'
                : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 hover:border-primary/30'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{cat.icon}</span>
              <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{cat.label}</span>
              <svg
                className={`w-3.5 h-3.5 ml-auto text-gray-400 transition-transform ${expanded === cat.label ? 'rotate-180' : ''}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </div>
          </button>
          {expanded === cat.label && (
            <div className="mt-2 space-y-1.5 pl-2 fade-in">
              {cat.questions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => onSelect(q)}
                  className="w-full text-left text-xs px-3 py-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-primary/5 dark:hover:bg-primary/10 hover:text-primary transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function MentorPage() {
  const { addToast } = useToast();
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [assessmentId, setAssessmentId] = useState<string>('');
  const [followUps, setFollowUps] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const sessionIdRef = useRef(`session-${Date.now()}`);
  const { user, loading: authLoading } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    inputRef.current?.focus();
    const storedId = sessionStorage.getItem('assessment_id');
    if (storedId) setAssessmentId(storedId);
  }, []);

  const parseSuggestions = useCallback((response: string): void => {
    const match = response.match(/\[SUGGESTIONS\]\s*([\s\S]*?)\s*\[\/SUGGESTIONS\]/);
    if (match) {
      const suggestions = match[1]
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0 && s.length < 150);
      setFollowUps(suggestions.slice(0, 3));
    } else {
      setFollowUps([]);
    }
  }, []);

  const send = async (question?: string) => {
    const text = (question || input).trim();
    if (!text || loading) return;

    const userMessage: MentorMessage = { role: 'user', content: text, timestamp: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setFollowUps([]);

    try {
      const data = await mentorChat(text, assessmentId);
      const rawResponse = data.response || 'I could not process that question. Please try again.';
      const cleanResponse = rawResponse.replace(/\[SUGGESTIONS\][\s\S]*?\[\/SUGGESTIONS\]/g, '').trim();
      const assistantMessage: MentorMessage = {
        role: 'assistant',
        content: cleanResponse,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      parseSuggestions(rawResponse);
    } catch {
      addToast({
        title: 'Error',
        description: 'Failed to send message. Please check your connection and try again.',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await clearMentorSession(sessionIdRef.current);
    } catch { /* ignore */ }
    sessionIdRef.current = `session-${Date.now()}`;
    setMessages([]);
    setFollowUps([]);
    addToast({ title: 'Chat Cleared', description: 'Conversation history has been cleared.', type: 'success' });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const formatTime = (ts?: number) => {
    if (!ts) return '';
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (authLoading) {
    return (
      <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex items-center justify-center">
        <div className="flex gap-1">
          <span className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex flex-col items-center justify-center fade-in text-center px-4">
        <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent/20 rounded-2xl flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Authentication Required</h1>
        <p className="text-gray-600 dark:text-gray-400 max-w-md mb-8">
          You need to be signed in to use the AI Career Mentor. This allows the mentor to remember your conversations and personalize advice.
        </p>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="px-6 py-3 rounded-xl bg-primary text-white font-semibold hover:bg-primary/90 transition-all shadow-lg shadow-primary/25"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-6 py-3 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white font-semibold hover:bg-gray-200 dark:hover:bg-gray-700 transition-all border border-gray-200 dark:border-gray-700"
          >
            Create Account
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex flex-col fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="page-title">AI Career Mentor</h1>
          <p className="page-subtitle">
            Ask anything about cybersecurity careers, skills, and certifications.
            {assessmentId && (
              <Badge variant="success" size="sm" className="ml-2">
                Assessment linked
              </Badge>
            )}
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearChat}>
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.992 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
            </svg>
            New Chat
          </Button>
        )}
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4" role="log" aria-label="Chat messages" aria-live="polite">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 002.455 2.456z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Hello! I&apos;m your AI Career Mentor</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
                I can help with career planning, certification advice, skill gaps, and learning strategies.
              </p>

              <TopicCategories onSelect={send} />

              <div className="flex flex-wrap justify-center gap-2 max-w-lg mx-auto">
                {MENTOR_SUGGESTED_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => send(q)}
                    className="text-left px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-primary/5 hover:border-primary/30 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} slide-up`}>
              {m.role === 'assistant' && (
                <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                  <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25" />
                  </svg>
                </div>
              )}
              <div className="max-w-[80%] group">
                <div
                  className={`
                    px-4 py-3 rounded-2xl leading-relaxed
                    ${m.role === 'user'
                      ? 'bg-primary text-white rounded-br-md'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
                    }
                  `}
                >
                  {m.role === 'assistant' ? (
                    <div
                      className="[&>p]:text-sm [&>p]:my-1 [&>ol]:text-sm [&>ol]:list-decimal [&>ol]:list-inside [&>ol]:space-y-1 [&>ol]:my-2 [&>ul]:text-sm [&>ul]:list-disc [&>ul]:list-inside [&>ul]:space-y-1 [&>ul]:my-2 [&>strong]:font-semibold"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }}
                    />
                  ) : (
                    <p className="text-sm whitespace-pre-line">{m.content}</p>
                  )}
                </div>
                <div className={`flex items-center gap-2 mt-1 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">{formatTime(m.timestamp)}</span>
                  {m.role === 'assistant' && <CopyButton text={m.content} />}
                </div>
              </div>
              {m.role === 'user' && (
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center ml-2 mt-1 flex-shrink-0">
                  <svg className="w-4 h-4 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0" />
                  </svg>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start slide-up">
              <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25" />
                </svg>
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {followUps.length > 0 && !loading && (
            <FollowUpSuggestions suggestions={followUps} onSelect={send} />
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about certifications, skills, career paths..."
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus-ring-offset-0 focus:ring-primary/20 focus:border-primary"
              disabled={loading}
              aria-label="Type your question"
            />
            <Button onClick={() => send()} disabled={loading || !input.trim()} aria-label="Send message">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
