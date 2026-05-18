import { useState, useEffect, useRef, FormEvent } from 'react';
import { ChatMessage, Intake } from '../types';
import { createSession, sendMessage, closeSession } from '../services/api';

export default function Chat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [intake, setIntake] = useState<Intake | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    startSession();
    return () => {
      if (sessionId) closeSession(sessionId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

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
      </form>
    </div>
  );
}
