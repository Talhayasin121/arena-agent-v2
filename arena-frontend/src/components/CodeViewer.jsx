import { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

export default function CodeViewer({ code, language = 'python', title = 'Source Code' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-viewer glass-card">
      <div className="code-header">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-accent" />
          <span className="text-xs font-bold uppercase tracking-wider opacity-70">{title}</span>
        </div>
        <button className="copy-button" onClick={handleCopy}>
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <div className="code-content">
        <pre><code className={`language-${language}`}>{code}</code></pre>
      </div>
    </div>
  );
}
