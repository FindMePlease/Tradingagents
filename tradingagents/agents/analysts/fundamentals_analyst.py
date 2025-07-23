# tradingagents/agents/fundamentals_analyst.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 假设您已经在 tradingagents/tools/ashare_tools.py 中定义了A股数据工具
# from tradingagents.tools.ashare_tools import (
#     get_ashare_income_statement,
#     get_ashare_balance_sheet,
#     get_ashare_cashflow_statement,
#     get_ashare_company_profile,
#     get_ashare_top10_shareholders
# )

def create_fundamentals_analyst(llm, toolkit):
    """
    创建一个为中国A股市场深度定制的基本面分析师智能体。
    """
    def fundamentals_analyst_node(state):
        """
        这是在LangGraph中运行的实际节点。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"] # 例如 '600519.SH'

        # --- A股改造第一步：替换数据工具 ---
        # 移除所有Finnhub/Simfin工具，换上我们为A股定制的工具。
        # 这些工具函数需要您在 toolkit 对象中实现，例如在 ashare_tools.py 中定义。
        tools = [
            toolkit.get_ashare_income_statement,      # 获取A股利润表
            toolkit.get_ashare_balance_sheet,       # 获取A股资产负债表
            toolkit.get_ashare_cashflow_statement,  # 获取A股现金流量表
            toolkit.get_ashare_company_profile,     # 获取A股公司基本信息
            toolkit.get_ashare_top10_shareholders   # 获取A股十大股东信息
        ]

        # --- A股改造第二步：重塑AI大脑 (系统提示词) ---
        # 这个提示词是整个改造的灵魂，它教会AI如何像中国分析师一样思考。
        system_message = (
            "你是一位顶级的中国A股市场基本面分析师，拥有20年从业经验，对A股的政策环境和公司财务特点有深刻的理解。你的任务是为交易员撰写一份专业、深入、有洞察力的基本面分析报告。"
            "你的分析必须超越简单的财务数据罗列，重点关注以下具有中国A股特色的关键领域：\n"
            "1.  **股权结构与公司背景**: 分析公司的控股股东性质（是国企还是民企？），前十大股东构成。这对于理解公司的治理结构和潜在资源至关重要。\n"
            "2.  **利润质量分析**: 深入利润表，特别审查'政府补助'占净利润的比重，评估其盈利的真实性和可持续性。同时关注'研发投入'的资本化比例，判断是否存在利润调节的可能。\n"
            "3.  **财务健康度**: 结合资产负债表，评估公司的资产质量和债务风险。特别关注主要股东的'股权质押'比例，高比例的质押可能预示着潜在的流动性风险。\n"
            "4.  **关联交易审查**: 检查是否存在大量的关联方交易，并评估这些交易的公允性及其对公司独立性的影响。\n"
            "5.  **政策与行业对齐度**: 结合公司简介和主营业务，分析公司所处行业是否与当前国家的核心政策（如'新质生产力'、'碳中和'等）高度契合。这是A股估值的核心驱动力之一。\n\n"
            "请使用你被赋予的工具来获取最新的财务数据和公司信息。你的最终报告需要结构清晰，首先是综合性的分析摘要，然后是上述各个要点的分项论述。最后，请在报告末尾附加一个Markdown表格，总结所有关键的财务指标和你的核心观点，使其一目了然。"
        )

        # --- 以下为LangChain和LangGraph的标准流程 ---
        prompt = ChatPromptTemplate.from_messages(
           
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        # 如果LLM没有调用工具而是直接生成了报告内容
        if not result.tool_calls and result.content:
            report = result.content
        # 如果LLM调用了工具，报告内容通常会在后续的节点中根据工具返回结果生成
        # 这里我们也可以先将初步的思考过程存入状态
        elif result.tool_calls:
            report = f"已调用工具 {', '.join([tc['name'] for tc in result.tool_calls])} 准备分析..."


        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node