# backend/app/main.py
import json
import re
from contextlib import asynccontextmanager
from typing import List, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入模块
from core.config import DATA_PATH
from core.llm_driver import call_llm_core
from modules.knowledge_base import load_knowledge, semantic_search
from modules.memory import SharedMemory
from agents.planner import PlannerAgent
from agents.executor import OceanExpertAgent
from agents.reviewer import ReviewerAgent


def clean_text(text: str) -> str:
    if not text:
        return ""
    # 1. 去掉星星(*)和井号(#)
    text = text.replace("*", "").replace("#", "")
    # 2. 去掉开头的奇怪符号，比如 "）]：" 或者 "："
    text = re.sub(r'^[）\]：: \s]+', '', text)
    return text.strip()


# === 1. 数据模型 (这里必须严格匹配前端 index.html) ===
class StepLog(BaseModel):
    step_id: int
    agent: str  # 前端要 agent，不要叫 role
    action: str  # 前端要 action
    input: str  # 前端要 input，不能丢
    output: str  # 前端要 output，不要叫 content


class RunResponse(BaseModel):
    final_answer: str
    steps: List[StepLog]  # 必须叫 steps


# === 2. 生命周期 ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"正在初始化系统，加载数据：{DATA_PATH}")
    load_knowledge(DATA_PATH)
    yield
    print("系统关闭。")


app = FastAPI(title="Ocean Agent System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 3. 核心接口 ===
@app.post("/api/run", response_model=RunResponse)
async def run_task(req: Dict[str, str]):
    user_query = req.get("query", "")
    logs = []

    # 初始化
    planner = PlannerAgent("Commander", "规划者", "拆解任务")
    expert = OceanExpertAgent("Dr.Ocean", "执行者", "具体分析")
    reviewer = ReviewerAgent("Critic", "审查者", "质量控制")
    memory = SharedMemory()

    # --- Step 1: 规划 ---
    # 记录：System Init
    logs.append(StepLog(
        step_id=0,
        agent="System",
        action="Init",
        input="Loading...",
        output="初始化智能体..."
    ))

    plan = planner.plan(user_query)

    # 记录：Planner
    logs.append(StepLog(
        step_id=1,
        agent="PlannerAgent",  # 对应前端显示名字
        action="TaskDecomposition",
        input=f"用户问题: {user_query}",
        output=json.dumps(plan, ensure_ascii=False)

    ))

    step_cnt = 2

    # --- Step 2: 循环执行 ---
    for task in plan:
        tool = task.get("tool")
        instr = task.get("instruction")

        # 2.1 检索
        if tool == "SEARCH":
            res = semantic_search(instr)
            clean_res = clean_text(res)
            memory.add_content("KnowledgeBase", res, "Retrieval")

            logs.append(StepLog(
                step_id=step_cnt,
                agent="KnowledgeBase",  # 前端显示
                action="SemanticSearch",
                input=f"检索关键词: {instr}",
                output=clean_res
            ))

        # 2.2 分析
        elif tool == "ANALYZE":
            current_context = memory.get_context()
            res = expert.execute(instr, current_context)
            clean_res = clean_text(res)
            memory.add_content("OceanExpert", res, "Analysis")

            logs.append(StepLog(
                step_id=step_cnt,
                agent="OceanExpert",
                action="Reasoning",
                input=f"分析指令: {instr}",
                output=clean_res
            ))

        # 2.3 报告与审查
        elif tool == "REPORT":
            current_context = memory.get_context()
            draft = call_llm_core("你是报告员", f"基于：{current_context}\n回答：{user_query}")
            clean_draft = clean_text(draft)
            # 先记录一下初稿
            logs.append(StepLog(
                step_id=step_cnt,
                agent="ReportAgent",
                action="Drafting",
                input="生成初稿",
                output=clean_draft
            ))
            step_cnt += 1

            # 自适应反馈闭环
            review = reviewer.review(draft, user_query)
            if review["status"]:
                logs.append(StepLog(
                    step_id=step_cnt,
                    agent="Reviewer",
                    action="QualityCheck",
                    input="审查初稿",
                    output="✅ 审查通过"
                ))
                memory.add_content("System", draft, "FinalReport")
            else:
                logs.append(StepLog(
                    step_id=step_cnt,
                    agent="Reviewer",
                    action="QualityCheck",
                    input="审查初稿",
                    output=f"❌ 驳回: {review['feedback']}"
                ))
                step_cnt += 1

                # 自动修正
                final = call_llm_core("你是修正专家", f"原稿：{draft}\n意见：{review['feedback']}\n请重写。")
                logs.append(StepLog(
                    step_id=step_cnt,
                    agent="SelfCorrection",
                    action="Refining",
                    input="根据意见修正",
                    output=final
                ))
                memory.add_content("System", final, "FinalReport")

        step_cnt += 1

    final_output = memory.get_context().split("FinalReport")[-1] if "FinalReport" in memory.get_context() else "任务完成"
    clean_final_output = clean_text(final_output)
    return RunResponse(final_answer=clean_final_output.strip(), steps=logs)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)