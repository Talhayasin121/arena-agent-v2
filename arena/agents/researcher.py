import asyncio
from typing import Optional, List
from arena.utils.llm import chat
from arena.utils.parser import AgentResult
from arena.tools.search import search

SYSTEM_PROMPT = """Research analyst. Answer based on search results."""

async def research(query, context="", feedback=None, verbose=False) -> AgentResult:
    results = await search(query, max_results=3)
    snippets = "\n".join([r["snippet"] for r in results])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Query: {query}\nResults: {snippets}"}]
    try:
        summary = await chat(messages, model="smart")
        return AgentResult(task_id="researcher", summary=summary, full_output=snippets, sources=[r["url"] for r in results])
    except: return AgentResult(task_id="researcher", summary="Error", full_output="Error")
