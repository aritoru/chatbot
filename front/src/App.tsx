import Chat from './components/Chat';

export default function App() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <h1 className="site-title">AD&amp;DHelp</h1>
        <p className="site-tagline">Consult the Sage — Your AD&amp;D Oracle</p>
      </header>
      <hr className="header-divider" />
      <Chat />
    </div>
  );
}
