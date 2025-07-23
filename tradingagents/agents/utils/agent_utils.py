# tradingagents/utils/agent_utils.py

# 导入必要的库
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage, RemoveMessage
from langchain_core.tools import tool
from typing import List, Annotated
import pandas as pd
import os
from datetime import datetime, timedelta

# 导入我们自己的模块
from tradingagents.default_config import DEFAULT_CONFIG
# 假设您已经创建了对接Tushare/Baostock的底层数据接口
import tradingagents.dataflows.ashare_interface as ashare_interface 
# 假设您已经集成了缠论计算库
import tradingagents.dataflows.chanlun_calculator as chanlun_calculator

# 保留原有的消息删除工具函数，它与市场无关
def create_msg_delete():
    def delete_messages(state):
        messages = state["messages"]
        removal_operations =
        placeholder = HumanMessage(content="继续")
        return {"messages": removal_operations + [placeholder]}
    return delete_messages

# --- A股改造核心：创建一个全新的A股工具箱 ---
class AshareToolkit:
    """
    一个为中国A股市场深度定制的、包含所有数据获取和计算工具的工具箱。
    所有智能体将通过调用这个类中的方法来获取A股市场的相关信息。
    """
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """更新类级别的配置"""
        cls._config.update(config)

    @property
    def config(self):
        """访问配置"""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)
        # 初始化A股数据接口 (例如，Tushare Pro API)
        # 确保您的Tushare Token已在配置文件或环境变量中设置
        ashare_interface.initialize_tushare(self.config.get("TUSHARE_TOKEN"))

    # --- A股特色工具集 ---

    @staticmethod
    @tool
    def get_ashare_daily_kline(
        ticker: Annotated,
        start_date: Annotated,
        end_date: Annotated,
    ) -> str:
        """
        获取指定A股股票在日期范围内的后复权日线行情数据。
        """
        df = ashare_interface.get_daily_kline(ticker, start_date, end_date)
        if df is None or df.empty:
            return f"未能获取到股票 {ticker} 的行情数据。"
        # 将DataFrame转换为对LLM友好的Markdown格式字符串
        return df.to_markdown()

    @staticmethod
    @tool
    def get_ashare_financial_report(
        ticker: Annotated,
        report_type: Annotated[str, "财报类型，必须是 'income' (利润表), 'balance' (资产负债表), 或 'cashflow' (现金流量表) 之一"],
        period: Annotated,
    ) -> str:
        """
        获取指定A股公司的单季财务报表。
        """
        df = ashare_interface.get_financial_statement(ticker, report_type, period)
        if df is None or df.empty:
            return f"未能获取到股票 {ticker} 的 {report_type} 财务报表。"
        return df.to_markdown()

    @staticmethod
    @tool
    def get_ashare_top10_shareholders(
        ticker: Annotated,
        period: Annotated,
    ) -> str:
        """
        获取指定A股公司在某个报告期的前十大股东信息，用于分析股权结构。
        """
        df = ashare_interface.get_top10_shareholders(ticker, period)
        if df is None or df.empty:
            return f"未能获取到股票 {ticker} 的十大股东信息。"
        return df.to_markdown()

    @staticmethod
    @tool
    def get_ashare_sina_news(
        ticker: Annotated,
        days_ago: Annotated[int, "查询过去多少天的新闻，例如 7"] = 7,
    ) -> str:
        """
        从主流财经门户（如新浪财经）获取与指定A股公司相关的最新新闻。
        """
        news_list = ashare_interface.fetch_sina_news(ticker, days_ago)
        if not news_list:
            return f"过去{days_ago}天内，没有找到关于 {ticker} 的重要新闻。"
        # 将新闻列表格式化为易于阅读的字符串
        return "\n".join([f"- {item['datetime']}: {item['title']}" for item in news_list])

    @staticmethod
    @tool
    def get_ashare_xueqiu_discussions(
        ticker: Annotated,
        days_ago: Annotated[int, "查询过去多少天的讨论，例如 7"] = 7,
    ) -> str:
        """
        从雪球(Xueqiu)社区获取关于指定A股公司的热门讨论帖子，用于分析投资者情绪。
        """
        discussions = ashare_interface.fetch_xueqiu_discussions(ticker, days_ago)
        if not discussions:
            return f"过去{days_ago}天内，雪球上没有关于 {ticker} 的热门讨论。"
        return "\n".join([f"- {post['user']}: {post['text']}" for post in discussions])

    @staticmethod
    @tool
    def get_ashare_chanlun_analysis(
        ticker: Annotated,
        frequency: Annotated,
        end_date: Annotated,
    ) -> str:
        """
        对指定A股股票进行缠论结构分析，返回当前的笔、线段和中枢状态。
        这是一个高级技术分析工具，用于识别市场结构和潜在买卖点。
        """
        # 1. 先获取行情数据
        kline_df = ashare_interface.get_daily_kline_for_chanlun(ticker, end_date)
        if kline_df is None or kline_df.empty:
            return f"无法获取行情数据，不能进行缠论分析。"
        
        # 2. 调用缠论计算器
        chanlun_result = chanlun_calculator.process(kline_df, frequency)
        if not chanlun_result:
            return "缠论分析失败。"
        # 将复杂的分析结果格式化为对LLM友好的文本摘要
        return json.dumps(chanlun_result, indent=2, ensure_ascii=False)