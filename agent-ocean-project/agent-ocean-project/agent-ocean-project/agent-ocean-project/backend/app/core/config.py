import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 找到项目根目录（防止找不到 .env 文件）
# 现在的路径是 backend/app/core/config.py，往上跳 3 级就是项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# 2. 尝试加载环境变量（钥匙）
print(f"🔑 [配置中心] 正在尝试加载配置文件: {ENV_PATH}")
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print("✅ 配置文件 .env 加载成功！")
else:
    print("⚠️ 没找到 .env 文件，不过没关系！我们将使用默认演示模式。")

# 3. 获取数据文件夹路径 (自动适配各种电脑)
DATA_PATH = BASE_DIR / "data"

# 4. 获取 API Key
# 核心逻辑：如果没有 key，就给一个空字符串，防止程序报错崩溃
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

# 5. 打印状态给太奶看
if not DEEPSEEK_API_KEY or "sk-" not in DEEPSEEK_API_KEY:
    print("🎭 [提示] 未检测到有效的 API Key，系统将自动切换到【Mock演示模式】。")
    print("    (这是正常的！不用担心，智能体依然会回答问题！)")
else:
    print("🚀 [提示] 检测到 API Key，系统将使用【真实大模型】进行推理。")