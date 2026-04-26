# Arena Sandbox
def run_in_sandbox(code: str):
    try:
        exec(code)
        return "Success"
    except Exception as e:
        return str(e)
