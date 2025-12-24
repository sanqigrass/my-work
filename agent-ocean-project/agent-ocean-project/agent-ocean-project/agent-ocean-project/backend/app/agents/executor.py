from core.llm_driver import call_llm_core
from .base import BaseAgent

class OceanExpertAgent(BaseAgent):
    def execute(self, instruction: str, context: str) -> str:
        return call_llm_core(
            system_prompt="你是海洋专家。基于提供的上下文数据回答指令。",
            user_prompt=f"指令：{instruction}\n\n数据：\n{context}"
        )