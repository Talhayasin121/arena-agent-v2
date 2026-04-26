import { useEffect, useState } from 'react';
import { marked } from 'marked';
import { FileText, Download, RotateCcw, Copy, Check, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function FinalReport({ report, runId, onRestart }) {
  const [html, setHtml] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (report) {
      marked.setOptions({ gfm: true, breaks: true, headerIds: true, mangle: false });
      setHtml(marked.parse(report));
    }
  }, [report]);

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ARENA-Report-${runId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadDoc = () => {
    const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Export HTML to Word</title></head><body>";
    const footer = "</body></html>";
    const sourceHTML = header + html + footer;
    const blob = new Blob(['\ufeff', sourceHTML], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ARENA-Report-${runId}.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="final-report glass-card mt-6">
      <div className="report-header">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-accent" />
          <h3 className="font-bold">Intelligence Synthesis</h3>
        </div>
        <div className="report-actions">
          <button className="action-button" onClick={handleCopy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          <button className="action-button" onClick={handleDownload}>
            <Download size={14} />
            <span>MD</span>
          </button>
          <button className="action-button" onClick={handleDownloadDoc}>
            <Download size={14} />
            <span>Word</span>
          </button>
          <button className="action-button restart" onClick={onRestart}>
            <RotateCcw size={14} />
            <span>Restart</span>
          </button>
        </div>
      </div>
      <div className="report-content custom-scrollbar" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}
