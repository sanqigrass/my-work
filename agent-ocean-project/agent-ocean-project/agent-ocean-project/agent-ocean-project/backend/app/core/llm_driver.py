import os
import time
import json
import random
import requests
from .config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# 这是一个开关，如果没有 Key，自动切换到“伪装模式”
USE_MOCK = not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def call_llm_core(system_prompt: str, user_prompt: str, temperature: float = 0.5) -> str:
    """
    核心 LLM 调用函数。
    包含 Mock 机制：如果没有 API Key，则返回模拟数据，保证系统不崩溃。
    """

    # -------------------------------------------------------
    # 模式 A：真实调用 (如果有 Key)
    # -------------------------------------------------------
    if not USE_MOCK:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1500
        }
        try:
            # 打印一下提示，让你知道真的在发请求
            print(f"📡 [Real API]正在调用 DeepSeek... (User: {user_prompt[:20]}...)")
            response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
            res_json = response.json()
            if "choices" in res_json:
                return res_json["choices"][0]["message"]["content"]
            print(f"API Error: {res_json}")
            return "ERROR: API调用异常"
        except Exception as e:
            return f"ERROR: {str(e)}"

    # -------------------------------------------------------
    # 模式 B：Mock 模拟 (如果没有 Key) - 你的救星
    # -------------------------------------------------------
    else:
        print(f"🎭 [Mock Mode] 正在模拟 AI 思考... (Prompt类型: {system_prompt[:10]}...)")
        time.sleep(1.5)  # 假装思考 1.5 秒，让前端效果更真实

        # 1. 模拟 Planner (规划者) 的返回
        # 必须返回合法的 JSON，否则程序会崩
        if "JSON" in system_prompt or "Task List" in system_prompt or "任务链" in system_prompt:
            return json.dumps([
                {
                    "step": 1,
                    "tool": "SEARCH",
                    "instruction": f"检索关于 '{user_prompt}' 的海洋数据"
                },
                {
                    "step": 2,
                    "tool": "ANALYZE",
                    "instruction": "根据检索到的数据，分析其对环境或生态的潜在影响"
                },
                {
                    "step": 3,
                    "tool": "REPORT",
                    "instruction": "汇总所有信息，生成一份简报"
                }
            ], ensure_ascii=False)

        # 2. 模拟 Reviewer (审查者) 的返回
        # 我们随机让它通过或失败，演示“自适应反馈”
        if "质量审查" in system_prompt or "PASS" in system_prompt:
            # 80% 概率通过，20% 概率驳回（为了演示效果）
            if random.random() > 0.2:
                return "PASS"
            else:
                return "我觉得分析还不够深入，特别是关于盐度变化的部分，请补充更多数据支持。"

        # 3. 模拟 Executor / Report (专家/报告) 的返回
        # 返回一些看起来很专业的假话
        return (
            f"【模拟AI回答】基于您的请求“{user_prompt}”，我的分析如下：\n"
            "1. 根据模拟检索，该海域深度 50m 处温度约为 24.5°C，盐度 34.2 PSU。\n"
            "2. 这种环境通常适合珊瑚礁生长，但也容易受厄尔尼诺现象影响。\n"
            "3. (这是一段由 Mock 驱动生成的测试文本，用于验证系统流程是否通畅。)"
        )