import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react';

export default function GoalInput() {
  const [goal, setGoal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!goal.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal }),
      });
      const data = await response.json();
      navigate(`/run/${data.run_id}`);
    } catch (error) {
      console.error('Failed to start run:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="goal-input-container" onSubmit={handleSubmit}>
      <div className="input-wrapper glass-card">
        <div className="sparkle-icon">
          <Sparkles size={20} />
        </div>
        <textarea
          className="goal-textarea"
          placeholder="Define your research goal (e.g., 'Analyze the impact of quantum computing on cybersecurity')"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={1}
        />
        <button 
          type="submit" 
          className="submit-button"
          disabled={!goal.trim() || isSubmitting}
        >
          {isSubmitting ? (
            <Loader2 className="animate-spin" size={20} />
          ) : (
            <>
              <span>Initialize ARENA</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
      <div className="input-hints">
        <span>Press Enter to start research</span>
        <span className="hint-dot" />
        <span>Try: "Plan a sustainable energy strategy for a small city"</span>
      </div>
    </form>
  );
}
