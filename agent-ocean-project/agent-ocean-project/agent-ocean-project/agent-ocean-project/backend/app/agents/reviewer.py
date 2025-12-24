from typing import Dict, Any
from core.llm_driver import call_llm_core
from .base import BaseAgent

class ReviewerAgent(BaseAgent):
    def review(self, content: str, goal: str) -> Dict[str, Any]:
        prompt = f"目标：{goal}\n内容：{content}\n是否合格？合格回 PASS，否则给出修改意见。"
        res = call_llm_core("你是质量审查员。", prompt, temperature=0.1)
        if "PASS" in res:
            return {"status": True, "feedback": "OK"}
        return {"status": False, "feedback": res}