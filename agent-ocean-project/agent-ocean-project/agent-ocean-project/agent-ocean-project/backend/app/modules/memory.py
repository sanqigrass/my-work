# backend/app/modules/memory.py
from typing import List, Dict, Any
import json


class SharedMemory:
    """
    黑板模式（Blackboard Pattern）的实现。
    负责在多智能体协同过程中存储、检索和管理共享上下文。
    """

    def __init__(self):
        # 短期记忆：用于通过 Prompt 传递给 LLM 的上下文
        self.short_term_context: str = ""

        # 结构化日志：用于前端展示或审计
        self.logs: List[Dict[str, Any]] = []

        # 事实数据槽：专门存放从数据库查出来的硬数据（可选扩展）
        self.artifacts: Dict[str, Any] = {}

    def add_content(self, role: str, content: str, action_type: str = "info"):
        """
        向共享记忆中添加一条新的交互记录
        """
        # 1. 更新结构化日志
        entry = {
            "role": role,
            "action": action_type,
            "content": content,
            "timestamp": "Now"  # 实际项目中可以用 datetime
        }
        self.logs.append(entry)

        # 2. 更新文本上下文 (LLM 实际看的内容)
        # 格式化一下，让 LLM 读起来更舒服
        formatted_entry = f"\n[{role} ({action_type})]: {content}"
        self.short_term_context += formatted_entry

    def get_context(self) -> str:
        """获取当前所有的上下文文本"""
        return self.short_term_context

    def get_recent_logs(self, limit: int = 5) -> List[Dict]:
        """获取最近的操作日志"""
        return self.logs[-limit:]

    def clear(self):
        """清空记忆（新任务开始时调用）"""
        self.short_term_context = ""
        self.logs = []