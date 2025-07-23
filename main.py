import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 这行代码会自动查找并加载项目根目录下的.env 文件
load_dotenv()

# 现在，您的程序就可以安全地读取这些密钥了
openai_key = os.getenv("OPENAI_API_KEY")
finnhub_key = os.getenv("FINNHUB_API_KEY")

# 您可以在这里打印一下来验证是否加载成功
if openai_key:
    print("成功从.env 文件加载 OpenAI API Key！")
else:
    print("未能加载 OpenAI API Key，请检查.env 文件是否存在于项目根目录。")
# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # Use a different model
config["backend_url"] = "https://generativelanguage.googleapis.com/v1"  # Use a different backend
config["deep_think_llm"] = "gemini-2.0-flash"  # Use a different model
config["quick_think_llm"] = "gemini-2.0-flash"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True  # Increase debate rounds

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
