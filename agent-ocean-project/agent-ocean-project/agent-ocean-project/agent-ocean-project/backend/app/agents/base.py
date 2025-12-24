from core.llm_driver import call_llm_core


class BaseAgent:
    def __init__(self, name: str, role: str, instruction: str):
        self.name = name
        self.role = role
        self.instruction = instruction

    def think(self, context: str) -> str:
        prompt = f"你是 {self.name}，{self.role}。\n任务：{self.instruction}\n\n上下文：\n{context}"
        return call_llm_core(prompt, "执行任务", temperature=0.3)