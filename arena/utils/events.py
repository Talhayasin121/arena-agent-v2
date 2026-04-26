import asyncio
import json

class EventEmitter:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def emit(self, event_type, data):
        await self.queue.put({"type": event_type, **data})

    async def task_started(self, agent, description, attempt=1):
        await self.emit("task_started", {"agent": agent, "description": description, "attempt": attempt})

    async def task_result(self, agent, task_id, summary):
        await self.emit("task_result", {"agent": agent, "task_id": task_id, "summary": summary})

    async def critic_score(self, score, issues, suggestion, passed):
        await self.emit("critic_score", {"score": score, "issues": issues, "suggestion": suggestion, "passed": passed})

    async def plan_created(self, data):
        await self.emit("plan_created", data)

    async def run_complete(self, report):
        await self.emit("run_complete", {"report": report})

    async def error(self, message):
        await self.emit("error", {"message": message})
    
    async def memory_stored(self, task_id):
        await self.emit("memory_stored", {"task_id": task_id})
    
    async def task_retrying(self, agent, attempt, feedback):
        await self.emit("task_retrying", {"agent": agent, "attempt": attempt, "feedback": feedback})
    
    async def task_failed(self, agent, task_id, reason):
        await self.emit("task_failed", {"agent": agent, "task_id": task_id, "reason": reason})
