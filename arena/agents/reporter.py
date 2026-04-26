from typing import List
from arena.utils.llm import chat
from arena.utils.parser import AgentResult

SYSTEM_PROMPT = """Synthesize research results into a high-quality report."""

async def synthesize(goal: str, results: List[AgentResult]) -> str:
    combined = "\n\n".join([r.summary for r in results])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Goal: {goal}\nResults: {combined}"}]
    try: return await chat(messages, model="smart")
    except: return combined
