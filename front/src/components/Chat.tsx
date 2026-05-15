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

  if (intake) {
    return (
      <div style={styles.container}>
        <div style={styles.completion}>
          <h2>Your issue has been submitted!</h2>
          <p>
            Reference number: <strong>{intake.issue_reference_number}</strong>
          </p>
          <p>Keep this number to follow up on your issue.</p>
          <div style={styles.intakeSummary}>
            <div>{intake.problem_description}</div>
          </div>
          <button style={styles.restartButton} onClick={() => { setIntake(null); setMessages([]); startSession(); }}>
            Start a new inquiry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <span>AD&amp;DHelp Support</span>
      </header>

      <div style={styles.messageList}>
        {messages.map((msg, i) => (
          <div key={i} style={msg.role === 'agent' ? styles.agentBubble : styles.customerBubble}>
            {msg.content}
          </div>
        ))}
        {loading && <div style={styles.agentBubble}>...</div>}
        {error && <div style={styles.errorBubble}>{error}</div>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={loading || !sessionId}
        />
        <button style={styles.sendButton} type="submit" disabled={loading || !sessionId}>
          Send
        </button>
      </form>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    maxWidth: 680,
    margin: '0 auto',
    fontFamily: 'system-ui, sans-serif',
    background: '#f9f9f9',
  },
  header: {
    padding: '12px 20px',
    background: '#7c3aed',
    color: '#fff',
    fontWeight: 600,
    fontSize: 16,
  },
  messageList: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  agentBubble: {
    alignSelf: 'flex-start',
    background: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '16px 16px 16px 4px',
    padding: '10px 14px',
    maxWidth: '80%',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
  },
  customerBubble: {
    alignSelf: 'flex-end',
    background: '#7c3aed',
    color: '#fff',
    borderRadius: '16px 16px 4px 16px',
    padding: '10px 14px',
    maxWidth: '80%',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
  },
  errorBubble: {
    alignSelf: 'center',
    background: '#fee2e2',
    color: '#991b1b',
    borderRadius: 8,
    padding: '8px 14px',
    fontSize: 13,
  },
  form: {
    display: 'flex',
    gap: 8,
    padding: '12px 20px',
    borderTop: '1px solid #e5e7eb',
    background: '#fff',
  },
  input: {
    flex: 1,
    padding: '10px 14px',
    borderRadius: 8,
    border: '1px solid #d1d5db',
    fontSize: 14,
    outline: 'none',
  },
  sendButton: {
    padding: '10px 20px',
    borderRadius: 8,
    background: '#7c3aed',
    color: '#fff',
    border: 'none',
    fontWeight: 600,
    cursor: 'pointer',
  },
  completion: {
    margin: '60px auto',
    padding: 32,
    background: '#fff',
    borderRadius: 12,
    border: '1px solid #e5e7eb',
    maxWidth: 480,
    textAlign: 'center',
  },
  intakeSummary: {
    textAlign: 'left',
    margin: '20px 0',
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    fontSize: 14,
    color: '#374151',
  },
  restartButton: {
    padding: '10px 20px',
    borderRadius: 8,
    background: '#7c3aed',
    color: '#fff',
    border: 'none',
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: 8,
  },
};
