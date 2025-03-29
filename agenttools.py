from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from tools import weather_tool, ArticleSummarizerTool

# 加載環境變數
load_dotenv()

# 創建 OpenAI 語言模型
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 修改提示模板
prompt = ChatPromptTemplate.from_messages([
    ('system', '''你是一位專業的台灣內容助理，具有以下能力：
    1. [天氣查詢] 可查詢台灣縣市天氣，需注意：
       - 縣市名稱必須使用繁體中文（如「臺北市」）
       - 自動將「台」轉換為「臺」
    2. [文章摘要] 可生成摘要並提取關鍵字，需注意：
       - 明確詢問用戶是否需要關鍵字分析
       - 摘要長度默認為100字

    回答時請保持簡潔、準確，並使用繁體中文。'''),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 初始化工具列表
tools = [weather_tool, ArticleSummarizerTool()]

# 創建智能代理
agent = create_tool_calling_agent(llm = llm,
                  tools = tools,
                  prompt = prompt,
                  )

# Create agent executor
agent_executor = AgentExecutor(agent = agent,
                 tools = tools,
                 verbose = True)


# 執行代理示例
def run_agent_example():
    article = """機器學習是人工智能的核心領域之一，它通過算法讓計算機從數據中學習規律。近年來，深度學習技術的突破大幅提升了圖像識別和自然語言處理的準確率。然而，機器學習模型需要大量高質量的訓練數據，數據不足會導致過擬合問題。此外，數據偏見也會影響模型公平性。研究者們正在探索小樣本學習和遷移學習等技術來降低數據依賴。未來，隨著算力提升和算法優化，機器學習將在醫療、金融等領域發揮更大價值。"""

    test_cases = [
        "你好嗎?",  # 基礎問答
        "臺北市今天天氣如何？",  # 天氣查詢
        "幫我摘要這篇文章：" + article,  # 摘要（無關鍵字）
        "請摘要這段文字並分析關鍵字：" + article, # 摘要+關鍵字
        "今天適合去台東縣玩嗎?",  # 測試自動轉換「台」→「臺」
    ]
    
    for query in test_cases:
        print(f"\n輸入查詢: {query}")
        result = agent_executor.invoke({"input": query})
        print(f"代理回應: {result['output']}")

if __name__ == "__main__":
    run_agent_example()
