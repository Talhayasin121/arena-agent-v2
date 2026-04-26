import { useState, useEffect } from 'react';
import { Database, Search, Trash2, Clock, Terminal, ChevronRight } from 'lucide-react';

export default function MemoryBrowser() {
  const [memories, setMemories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    fetch('/api/memory')
      .then(res => res.json())
      .then(data => setMemories(data));
  }, []);

  const filtered = memories.filter(m => 
    m.task_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="memory-page">
      <div className="memory-header">
        <div className="header-info">
          <h2><Database size={24} className="text-accent" /> Knowledge Base</h2>
          <p>Browsing {memories.length} neural associations</p>
        </div>
        <div className="search-bar glass-card">
          <Search size={18} className="text-muted" />
          <input 
            type="text" 
            placeholder="Search memory..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="memory-grid">
        <div className="memory-sidebar custom-scrollbar">
          {filtered.map(entry => (
            <div 
              key={entry.id} 
              className={`memory-entry ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
              onClick={() => setSelectedEntry(entry)}
            >
              <div className="entry-header">
                <span className="entry-agent">{entry.agent || 'Neural'}</span>
                <span className="entry-time"><Clock size={12} /> {new Date(entry.timestamp).toLocaleDateString()}</span>
              </div>
              <h4 className="entry-task">{entry.task_description}</h4>
              <p className="entry-preview">{entry.content.substring(0, 100)}...</p>
            </div>
          ))}
        </div>
        <div className="memory-viewer glass-card">
          {selectedEntry ? (
            <div className="viewer-content">
              <h3>{selectedEntry.task_description}</h3>
              <div className="entry-meta">
                <span>ID: {selectedEntry.id}</span>
                <span>Run: {selectedEntry.run_id}</span>
              </div>
              <div className="full-content custom-scrollbar">
                <pre>{selectedEntry.content}</pre>
              </div>
            </div>
          ) : (
            <div className="viewer-empty">
              <Database size={48} className="opacity-10" />
              <p>Select a memory fragment to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
