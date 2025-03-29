from langchain.tools import BaseTool, StructuredTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import re
import requests

# 函數式寫法(StructuredTool.from_function)：由 LangChain 内部自動生成 args_schema

# 定義天氣查詢工具的輸入格式
def get_weather(city: str = Field(description="臺灣縣市名稱（需繁體中文，如'臺北市'），系統會自動將「台」轉換為「臺」並補上「市」或「縣」")) -> str:
    """根據輸入的城市名稱查詢天氣資料"""
    # 使用 Google Apps Script 的 API 來獲取天氣資料
    response = requests.get(
        'https://script.google.com/macros/s/AKfycbwK-D0X0tB_P5KjEU-Wi9R1Oc5ZwIUUM41b9zZnt-Qti-IujrAtKe4RivAPPBhpZfkR2A/exec',
        params={'cityName': city}
    )
    if response.status_code == 200:
        try:
            return response.json()
        except requests.JSONDecodeError:
            return {"error": "回應不是有效的 JSON 格式"}
    else:
        return {"error": f"請求失敗，狀態碼: {response.status_code}"}
    
# 創建天氣查詢工具
weather_tool = StructuredTool.from_function(
    func = get_weather,
    name = "weather_tool",
    description = "根據輸入的臺灣縣市查詢天氣資料",
)


# 類別式寫法（BaseTool + BaseModel）:透過 BaseModel 統一管理參數規則

# 定義文章摘要工具的輸入格式
class ArticleInput(BaseModel):
    """文章摘要工具的輸入格式"""
    text: str = Field(description="要進行摘要的文章內容")
    max_length: int = Field(description="摘要的最大字數", default=100)
    keywords: bool = Field(description="是否包含關鍵字分析", default=False)

# 定義文章摘要工具
class ArticleSummarizerTool(BaseTool):
    """文章摘要工具"""
    name: str = "article_summarizer"
    description: str = "生成文章摘要，可選擇是否包含關鍵字分析"
    args_schema: Type[BaseModel] = ArticleInput
    
    def _extract_keywords(self, text: str) -> list:
        """提取關鍵字"""
        # 這裡使用簡單的實現，實際應用中可以使用更複雜的算法
        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # 只考慮長度大於3的詞
                word_freq[word] = word_freq.get(word, 0) + 1
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _create_summary(self, text: str, max_length: int) -> str:
        """生成摘要"""
        # 簡單實現，實際應用中可以使用更複雜的算法
        sentences = text.split('。')
        summary = '。'.join(sentences[:3])  # 取前三句
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        return summary
    
    def _run(self, text: str, max_length: int = 100, keywords: bool = False) -> str:
        """執行摘要生成"""
        try:
            summary = self._create_summary(text, max_length)
            if keywords:
                top_keywords = self._extract_keywords(text)
                keywords_str = ', '.join([f"{word}({freq}次)" for word, freq in top_keywords])
                return f"摘要：{summary}\n\n關鍵字：{keywords_str}"
            return f"摘要：{summary}"
        except Exception as e:
            return f"摘要生成錯誤: {str(e)}"
    
    async def _arun(self, text: str, max_length: int = 100, keywords: bool = False) -> str:
        """非同步執行"""
        return self._run(text, max_length, keywords)


