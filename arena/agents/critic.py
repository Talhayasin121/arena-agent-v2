from typing import Optional
from arena.utils.llm import chat
from arena.utils.parser import parse_critic_result, CriticResult

SYSTEM_PROMPT = """You are an auditor. Evaluate the output for accuracy and completeness.
Score from 1-10. If score < 7, provide suggestions for improvement.
Output JSON: {"score": 8, "issues": [], "suggestion": "", "passed": true}"""

async def evaluate(task: str, output: str) -> CriticResult:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Task: {task}\nOutput: {output}"}]
    try:
        response = await chat(messages, model="smart")
        return parse_critic_result(response)
    except: return CriticResult(score=5, issues=["Parsing error"], suggestion="Try again", passed=False)
