import asyncio
import os
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from arena.agents.planner import plan
from arena.agents.researcher import research
from arena.agents.coder import generate_code, execute_and_debug
from arena.agents.critic import evaluate
from arena.agents.memory import memory
from arena.agents.reporter import synthesize
from arena.utils.parser import TaskList, Task, AgentResult
from arena.utils.events import EventEmitter
from arena.utils.llm import chat

console = Console()

async def run(
    goal: str,
    run_id: str,
    emit: Optional[EventEmitter] = None,
    settings: Optional[Dict[str, Any]] = None,
    verbose: bool = False
) -> str:
    """Main orchestrator loop."""
    if settings is None:
        settings = {
            "max_retries": 1,
            "critic_threshold": 7,
            "max_tasks": 5,
            "provider": "gemini" if os.getenv("GOOGLE_API_KEY") else "nvidia"
        }
    
    max_retries = settings.get("max_retries", 1)
    critic_threshold = settings.get("critic_threshold", 7)
    max_tasks = settings.get("max_tasks", 5)
    
    if emit is None:
        class DummyEmitter:
            async def emit(self, event): pass
            async def plan_created(self, *args, **kwargs): pass
            async def task_started(self, *args, **kwargs): pass
            async def task_result(self, *args, **kwargs): pass
            async def critic_score(self, *args, **kwargs): pass
            async def task_retrying(self, *args, **kwargs): pass
            async def memory_stored(self, *args, **kwargs): pass
            async def task_failed(self, *args, **kwargs): pass
            async def run_complete(self, *args, **kwargs): pass
            async def error(self, *args, **kwargs): pass
        emit = DummyEmitter()
    
    results: List[AgentResult] = []
    
    # 1. PLAN
    await emit.task_started("planner", goal, 1)
    try:
        task_list = await plan(goal)
        if not task_list:
            await emit.error("Failed to create task plan")
            return "Error: Failed to create task plan"
        
        await emit.task_result("planner", "plan", f"Created {len(task_list.tasks)} tasks")
        await emit.plan_created({"goal": goal, "tasks": [t.model_dump() for t in task_list.tasks]})
    except Exception as e:
        await emit.error(f"Planner failed: {str(e)}")
        return f"Error: {str(e)}"

    # Process tasks
    for task in task_list.tasks[:max_tasks]:
        retries = 0
        feedback = None
        task_completed = False
        
        while retries <= max_retries and not task_completed:
            # 2. RETRIEVE MEMORY
            try:
                context = await memory.retrieve(task.description, top_k=3)
                context_str = "\n".join(context) if context else ""
            except:
                context_str = ""

            # 3. EXECUTE
            await emit.task_started(task.agent, task.description, retries + 1)
            
            try:
                if task.agent == "researcher":
                    result_obj = await research(task.description, context_str, feedback, verbose)
                elif task.agent == "coder":
                    result_obj = await run_coder_task(task.description, context_str, feedback, verbose)
                elif task.agent == "reporter":
                    intermediate_report = await synthesize(task.description, results)
                    result_obj = AgentResult(task_id=task.id, summary=f"Synthesized report", full_output=intermediate_report)
                else:
                    result_obj = await research(task.description, context_str, feedback, verbose)
                
                await emit.task_result(task.agent, task.id, result_obj.summary)
                
            except Exception as e:
                result_obj = AgentResult(task_id=task.id, summary=f"Failed: {str(e)}", full_output=str(e))
                await emit.task_result(task.agent, task.id, result_obj.summary)

            # 4. CRITIQUE
            try:
                critique = await evaluate(task.description, result_obj.full_output)
                await emit.critic_score(critique.score, critique.issues, critique.suggestion, critique.passed)
                
                if critique.passed or retries >= max_retries:
                    # STORE MEMORY
                    await memory.store(task.description, result_obj.full_output, {"run_id": run_id, "task_id": task.id})
                    await emit.memory_stored(task.id)
                    results.append(result_obj)
                    task_completed = True
                else:
                    retries += 1
                    feedback = critique.suggestion
                    await emit.task_retrying(task.agent, retries, feedback)
            except:
                results.append(result_obj)
                task_completed = True

    # 6. FINAL REPORT
    report = await synthesize(goal, results)
    await emit.run_complete(report)
    return report

async def run_coder_task(task, context, feedback, verbose):
    code = await generate_code(task, context, feedback, verbose)
    if not code: return AgentResult(task_id="coder", summary="Failed", full_output="Failed")
    stdout, stderr, success = await execute_and_debug(code, task, max_attempts=3, verbose=verbose)
    return AgentResult(task_id="coder", summary=f"Success: {stdout[:100]}", full_output=stdout, code=code, code_output=stdout)
