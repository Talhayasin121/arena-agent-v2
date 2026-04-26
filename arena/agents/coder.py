from typing import Optional, List
from arena.utils.llm import chat
from arena.utils.parser import AgentResult

SYSTEM_PROMPT = """You are a software engineer. Write Python code to solve the user's task.
Output only the Python code inside ```python``` fences."""

async def generate_code(task: str, context: str, feedback: Optional[str] = None, verbose: bool = False) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Task: {task}\nContext: {context}"}]
    if feedback: messages.append({"role": "user", "content": f"Feedback: {feedback}"})
    try:
        response = await chat(messages, model="code")
        import re
        match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
        return match.group(1) if match else response
    except: return ""

async def execute_and_debug(code: str, task: str, max_attempts: int = 3, verbose: bool = False):
    import sys
    from io import StringIO
    
    stdout_capture = StringIO()
    sys.stdout = stdout_capture
    try:
        exec(code, {})
        output = stdout_capture.getvalue()
        return output, "", True
    except Exception as e:
        return "", str(e), False
    finally:
        sys.stdout = sys.__stdout__
