import asyncio
from typing import Optional
from arena.utils.llm import chat
from arena.utils.parser import parse_task_list, TaskList

SYSTEM_PROMPT = """You are the Architect Agent for ARENA. Decompose user goals into 3-5 sequential tasks.
Agents: researcher, coder, reporter.
Output JSON: {"tasks": [{"id": "1", "description": "...", "agent": "...", "priority": 1, "depends_on": []}]}"""

async def plan(goal: str, verbose: bool = False) -> Optional[TaskList]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": goal}]
    try:
        response = await chat(messages, model="smart")
        return parse_task_list(response)
    except: return None
