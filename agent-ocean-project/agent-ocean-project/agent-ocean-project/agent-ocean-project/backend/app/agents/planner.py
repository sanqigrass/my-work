# backend/app/agents/planner.py
import json
import re
from typing import List, Dict
from core.llm_driver import call_llm_core
from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    def plan(self, user_query: str) -> List[Dict]:
        sys_prompt = (
            "你是海洋任务规划专家。请将用户问题拆解为 2-4 个执行步骤。\n"
            "可用工具：\n"
            "1. tool: 'SEARCH', instruction: '搜索关键词' (用于获取数据)\n"
            "2. tool: 'ANALYZE', instruction: '分析要求' (用于基于数据推理)\n"
            "3. tool: 'REPORT', instruction: '总结要求' (最后一步)\n\n"
            "【严格输出格式】：必须是纯 JSON 列表（Array），不要包含 Markdown 代码块（```json）。\n"
            "示例：\n"
            '[{"step": 1, "tool": "SEARCH", "instruction": "南海 深层 温度"}, {"step": 2, "tool": "ANALYZE", "instruction": "分析温度特征"}]'
        )

        raw_response = call_llm_core(sys_prompt, f"任务目标：{user_query}", temperature=0.1)

        # === JSON 清洗逻辑 (核心修复) ===
        try:
            # 1. 尝试去掉 markdown 代码块标记
            cleaned = raw_response.replace("```json", "").replace("```", "").strip()

            # 2. 如果还有废话，尝试提取 [] 里的内容
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                cleaned = match.group()

            # 3. 解析
            plan = json.loads(cleaned)

            # 4. 简单的校验：确保解析出来是列表
            if isinstance(plan, list):
                print(f"✅ Planner 规划成功: {len(plan)} 个步骤")
                return plan
            else:
                print("⚠️ Planner 返回了 JSON 但不是列表")

        except json.JSONDecodeError:
            print(f"❌ JSON 解析失败，模型原生返回: {raw_response}")

        # === 兜底方案 (防止系统崩溃) ===
        # 如果模型实在太笨，解析失败了，为了不让演示挂掉，手动返回一个通用计划
        print("🔄 启用兜底计划...")
        return [
            {"step": 1, "tool": "SEARCH", "instruction": user_query},
            {"step": 2, "tool": "ANALYZE", "instruction": "基于检索数据回答问题"},
            {"step": 3, "tool": "REPORT", "instruction": "生成总结报告"}
        ]