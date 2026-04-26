import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, CheckCircle, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import CodeViewer from './CodeViewer';

export default function AgentFeed({ runId, onAgentChange, onComplete }) {
  const [events, setEvents] = useState([]);
  const feedRef = useRef(null);

  useEffect(() => {
    if (!runId) return;

    const eventSource = new EventSource(`/api/events/${runId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'task_started') {
        onAgentChange(data.agent);
      }
      
      if (data.type === 'run_complete') {
        onComplete(data.report);
      }
      
      setEvents(prev => [...prev, data]);
    };

    return () => eventSource.close();
  }, [runId]);

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [events]);

  const renderEvent = (event, index) => {
    const { type, agent, description, summary, score, passed, report } = event;
    
    switch (type) {
      case 'task_started':
        return (
          <div key={index} className="event-item task-start">
            <div className={`agent-indicator ${agent}`} />
            <div className="event-content">
              <span className="event-tag">DEPLOYING {agent.toUpperCase()}</span>
              <p>{description}</p>
            </div>
          </div>
        );
      case 'task_result':
        return (
          <div key={index} className="event-item task-result">
            <div className="event-icon success"><CheckCircle size={16} /></div>
            <div className="event-content">
              <span className="event-tag success">RESULT ACQUIRED</span>
              <p className="summary-text">{summary}</p>
            </div>
          </div>
        );
      case 'critic_score':
        return (
          <div key={index} className="event-item audit">
            <div className={`event-icon ${passed ? 'success' : 'warning'}`}>
              {passed ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            </div>
            <div className="event-content">
              <span className={`event-tag ${passed ? 'success' : 'warning'}`}>AUDIT COMPLETE - SCORE: {score}/10</span>
              <p>{passed ? 'Data validated. Proceeding to next phase.' : 'Refining output based on quality benchmarks...'}</p>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="agent-feed custom-scrollbar" ref={feedRef}>
      <div className="feed-container">
        {events.length === 0 && (
          <div className="feed-empty">
            <RefreshCw className="spinning" size={32} />
            <p>Initializing Neural Core...</p>
          </div>
        )}
        <AnimatePresence>
          {events.map((event, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderEvent(event, i)}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
