import requests
import os
from dotenv import load_dotenv

# 1. 加载您的钥匙
load_dotenv(".env")
api_key = os.getenv("DEEPSEEK_API_KEY")
api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

print("--------------------------------------------------")
print(f"🔑 正在检查钥匙: {api_key[:5]}******" if api_key else "❌ 没读到钥匙！请检查 .env 文件")
print(f"🌐 正在检查地址: {api_url}")
print("--------------------------------------------------")

if not api_key:
    print("❌ 错误：没有检测到 API Key，请先在 .env 文件里填好。")
    exit()

# 2. 发送一个最简单的测试请求
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "测试一下，你能听到吗？"}],
    "max_tokens": 10
}

try:
    print("🚀 正在尝试连接 DeepSeek 服务器...")
    response = requests.post(api_url, json=data, headers=headers, timeout=10)

    # 3. 分析结果
    print(f"📡 服务器返回状态码: {response.status_code}")

    if response.status_code == 200:
        print("✅ 成功！连通性完美！")
        print("🤖 模型回复:", response.json()['choices'][0]['message']['content'])
    elif response.status_code == 401:
        print("❌ 认证失败 (401)")
        print("原因：Key 不对。请检查有没有复制多余的空格？或者 Key 是不是被删了？")
    elif response.status_code == 402:
        print("❌ 余额不足 (402)")
        print("原因：账号里没钱了。新注册用户虽然有送，但有时候需要去官网“充值”页面看一眼激活一下。")
    else:
        print("❌ 其他错误")
        print("详细信息:", response.text)

except Exception as e:
    print("❌ 网络连不上！")
    print(f"错误原因: {e}")
    print("建议：如果您开了VPN，请尝试关掉；或者您的公司/学校网络屏蔽了 DeepSeek。")