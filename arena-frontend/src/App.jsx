import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Database, Settings as SettingsIcon, Brain } from 'lucide-react';
import GoalInput from './components/GoalInput';
import AgentFeed from './components/AgentFeed';
import TaskTracker from './components/TaskTracker';
import FinalReport from './components/FinalReport';
import MemoryBrowser from './components/MemoryBrowser';
import Settings from './components/Settings';
import RecentRuns from './components/RecentRuns';
import ProcessMap from './components/ProcessMap';
import { useStream } from './hooks/useStream';
import { useState, useEffect } from 'react';

function Navbar() {
  const location = useLocation();
  
  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">
        <div className="logo-icon">
          <Brain size={24} />
        </div>
        <span>ARENA</span>
      </Link>
      <div className="nav-links">
        <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
          <Home size={18} />
          <span>Home</span>
        </Link>
        <Link to="/memory" className={`nav-link ${location.pathname === '/memory' ? 'active' : ''}`}>
          <Database size={18} />
          <span>Memory</span>
        </Link>
        <Link to="/settings" className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`}>
          <SettingsIcon size={18} />
          <span>Settings</span>
        </Link>
      </div>
    </nav>
  );
}

function HomeView() {
  return (
    <div className="home-view">
      <div className="hero-section">
        <div className="hero-text">
          <h1>Intelligence <span>Redefined</span></h1>
          <p>The ultimate autonomous research agent for complex problem solving.</p>
        </div>
        <GoalInput />
      </div>
      <div className="home-content">
        <RecentRuns />
      </div>
    </div>
  );
}

function RunView() {
  const { runId } = useStream();
  const [activeAgent, setActiveAgent] = useState('');
  const [goal, setGoal] = useState('');
  const [status, setStatus] = useState('running');
  const [report, setReport] = useState(null);

  useEffect(() => {
    // Fetch initial run data
    if (runId) {
      fetch(`/api/run/${runId}`)
        .then(res => res.json())
        .then(data => {
          setGoal(data.goal);
          if (data.status === 'complete') {
            setStatus('complete');
            setReport(data.report);
          }
        });
    }
  }, [runId]);

  return (
    <div className="run-view">
      <div className="run-header">
        <div className="flex items-center gap-4">
          <Link to="/" className="back-link">
            <Home size={16} />
          </Link>
          <div className="run-title">
            <span className="run-id">ARENA Run #{runId?.slice(0, 8)}</span>
            <div className="run-status-badge">
              <span className={`status-dot ${status}`}></span>
              {status === 'running' ? 'LIVE' : 'COMPLETE'}
            </div>
          </div>
        </div>
        <h2 className="current-goal">{goal}</h2>
      </div>

      <ProcessMap activeAgent={activeAgent} />

      <div className="run-layout">
        <div className="run-main">
          <AgentFeed runId={runId} onAgentChange={setActiveAgent} onComplete={(rep) => {
            setReport(rep);
            setStatus('complete');
          }} />
        </div>
        <div className="run-sidebar">
          <TaskTracker runId={runId} />
          {report && <FinalReport report={report} runId={runId} onRestart={() => window.location.href = '/'} />}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomeView />} />
            <Route path="/run/:runId" element={<RunView />} />
            <Route path="/memory" element={<MemoryBrowser />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
