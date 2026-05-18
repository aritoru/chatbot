import { useState, useEffect, useRef, FormEvent } from 'react';
import { ChatMessage, Intake } from '../types';
import { createSession, sendMessage, closeSession } from '../services/api';

const ttsSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

const LOCALE_MAP: Record<string, string> = {
  en: 'en-GB',
  es: 'es-ES',
  fr: 'fr-FR',
  it: 'it-IT',
};

export default function Chat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [intake, setIntake] = useState<Intake | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [muted, setMuted] = useState(false);
  const [language, setLanguage] = useState('en');
  const bottomRef = useRef<HTMLDivElement>(null);
  const voiceRef = useRef<SpeechSynthesisVoice | null>(null);

  // Start session on mount; close on unmount
  useEffect(() => {
    startSession();
    return () => {
      if (sessionId) closeSession(sessionId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Scroll to bottom on new messages or loading state
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Select preferred TTS voice on mount and when language changes; re-select if voices load asynchronously (Chrome)
  useEffect(() => {
    if (!ttsSupported) return;
    pickVoice(language);
    const handler = () => pickVoice(language);
    window.speechSynthesis.addEventListener('voiceschanged', handler);
    return () => window.speechSynthesis.removeEventListener('voiceschanged', handler);
  }, [language]);

  // Narrate each new Agent message.
  // setTimeout(0) defers speak() past React 18 StrictMode's synchronous
  // cleanup-then-remount cycle, which otherwise cancels speech immediately.
  useEffect(() => {
    if (!ttsSupported || muted || messages.length === 0) return;
    const last = messages[messages.length - 1];
    if (last.role !== 'agent') return;

    const id = setTimeout(() => {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(last.content);
      utterance.rate = 0.88;
      utterance.pitch = 0.9;
      if (voiceRef.current) utterance.voice = voiceRef.current;
      window.speechSynthesis.speak(utterance);
    }, 0);

    return () => {
      clearTimeout(id);
      window.speechSynthesis.cancel();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  function pickVoice(lang = language) {
    if (!ttsSupported) return;
    const voices = window.speechSynthesis.getVoices();
    const locale = LOCALE_MAP[lang] ?? 'en-GB';
    const localeMatch = voices.find((v) => v.lang.startsWith(locale.split('-')[0]));
    const englishFallback = voices.find(
      (v) => /Daniel|George|Arthur/i.test(v.name) || v.lang.startsWith('en-GB'),
    );
    voiceRef.current = localeMatch ?? englishFallback ?? null;
  }

  function handleMuteToggle() {
    const nextMuted = !muted;
    if (nextMuted && ttsSupported) window.speechSynthesis.cancel();
    setMuted(nextMuted);
  }

  async function startSession() {
    setLoading(true);
    setError(null);
    try {
      const { session_id, message } = await createSession();
      setSessionId(session_id);
      setMessages([{ role: 'agent', content: message }]);
    } catch {
      setError('Could not connect to the server. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || !sessionId || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'customer', content: text }]);
    setLoading(true);
    setError(null);

    try {
      const res = await sendMessage(sessionId, text);
      setMessages((prev) => [...prev, { role: 'agent', content: res.message }]);
      if (res.language && res.language !== language) setLanguage(res.language);
      if (res.intake) {
        setIntake(res.intake);
        setSessionId(null);
      }
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleRestart() {
    if (ttsSupported) window.speechSynthesis.cancel();
    setIntake(null);
    setMessages([]);
    startSession();
  }

  if (intake) {
    return (
      <div className="page-container">
        <div className="confirmation-scroll">
          <h2 className="scroll-title">Your Inquiry Has Been Recorded</h2>
          <div className="scroll-irn">
            <span className="irn-label">Your Reference Scroll:</span>
            <strong className="irn-value">{intake.issue_reference_number}</strong>
          </div>
          <p className="scroll-desc">{intake.problem_description}</p>
          <button className="btn-new-consultation" onClick={handleRestart}>
            Begin a New Consultation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((msg, i) => (
          <div key={i} className={`msg-bubble ${msg.role === 'agent' ? 'msg-agent' : 'msg-customer'}`}>
            {msg.role === 'agent' && <span className="agent-label">⚗ The Sage</span>}
            <span>{msg.content}</span>
          </div>
        ))}
        {loading && (
          <div className="msg-bubble msg-agent msg-loading">
            <span className="agent-label">⚗ The Sage</span>
            <span className="loading-rune">✦</span>
          </div>
        )}
        {error && <div className="msg-error">{error}</div>}
        <div ref={bottomRef} />
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          className="input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Speak your query to the Sage..."
          disabled={loading || !sessionId}
        />
        <button className="btn-send" type="submit" disabled={loading || !sessionId}>
          Speak ᛦ
        </button>
        {ttsSupported && (
          <button
            className={`btn-mute${muted ? ' muted' : ''}`}
            type="button"
            onClick={handleMuteToggle}
            title={muted ? 'Unmute Sage' : 'Mute Sage'}
          >
            {muted ? '🔇' : '🔊'}
          </button>
        )}
      </form>
    </div>
  );
}
