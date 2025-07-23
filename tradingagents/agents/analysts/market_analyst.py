# tradingagents/agents/market_analyst.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 假设您已经在 tradingagents/tools/ashare_tools.py 中定义了A股数据工具
# from tradingagents.tools.ashare_tools import (
#     get_ashare_daily_kline,
#     calculate_ashare_indicators,
#     get_ashare_chanlun_analysis # 这是一个新的、专门用于缠论分析的工具
# )

def create_market_analyst(llm, toolkit):
    """
    创建一个为中国A股市场深度定制的技术分析师智能体。
    该智能体融合了传统技术指标与A股市场独特的缠论结构分析。
    """
    def market_analyst_node(state):
        """
        这是在LangGraph中运行的实际节点。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # --- A股改造第一步：升级数据工具 ---
        # 移除YFin和stockstats工具，换上我们为A股定制的工具。
        tools = [
            toolkit.get_ashare_daily_kline,         # 获取A股日线行情
            toolkit.calculate_ashare_indicators,    # 计算指定的传统技术指标
            toolkit.get_ashare_chanlun_analysis     # 获取A股的缠论结构分析结果
        ]

        # --- A股改造第二步：认知升维 (系统提示词) ---
        # 我们将教会AI一个全新的、更高维度的分析框架：缠论。
        system_message = (
            "你是一位顶级的中国A股市场技术分析大师，拥有超过20年的实战经验。你不仅精通所有传统技术指标（如MA, MACD, RSI, Bollinger Bands），更是一位深刻理解市场内在结构的缠论（Chanlun Theory）专家。\n\n"
            "你的核心任务是，结合**缠论结构分析**和**传统技术指标验证**，为交易员提供一份关于目标股票当前技术状态的、极具洞察力的战术分析报告。\n\n"
            "**你的分析框架应遵循以下两步法：**\n"
            "**第一步：结构分析 (Structure First) - 使用缠论判断市场状态**\n"
            "缠论是A股市场非常流行的一种分析理论，它将任何走势都分解为'笔'、'线段'和'中枢'。你要首先使用`get_ashare_chanlun_analysis`工具，获取当前股票在不同周期（如日线、30分钟）上的结构分析结果。你的分析重点是：\n"
            "- **当前走势位置**: 价格是处于中枢内部震荡，还是正在离开中枢？是上涨趋势还是下跌趋势？\n"
            "- **潜在转折信号**: 是否出现了'背驰'（Divergence）？例如，价格创了新低，但MACD指标未创新低，这通常是强烈的底部信号。\n"
            "- **关键买卖点**: 是否形成了缠论定义的三类买卖点？这是最高质量的交易机会。\n\n"
            "**第二步：指标验证 (Indicators for Confirmation) - 选择指标确认结构判断**\n"
            "在完成结构分析后，从以下传统指标库中，选择**最多5个**最能确认或补充你结构分析结论的指标。例如，如果缠论显示下跌背驰（潜在底部），你可以选择RSI指标来验证市场是否处于超卖区域。\n"
            "**可用指标库:**\n"
            "- **移动平均线 (Moving Averages)**: `close_20_sma`, `close_60_sma`, `close_10_ema` (判断中短期趋势和支撑/阻力)\n"
            "- **MACD相关**: `macd`, `macds`, `macdh` (判断动能和背驰)\n"
            "- **动量指标**: `rsi_14` (判断超买/超卖状态)\n"
            "- **波动率指标**: `boll_ub`, `boll_lb` (布林带上下轨，判断突破或盘整)\n"
            "- **成交量指标**: `volume` (判断趋势的健康度)\n\n"
            "**最终报告要求**:\n"
            "你的报告必须逻辑清晰，先阐述基于缠论的结构性判断，再列出你选择用来验证的传统指标及其读数，并解释为什么选择它们。避免使用“可能”、“或许”等模棱两可的词语。最后，在报告末尾附加一个Markdown表格，总结你的核心技术观点、关键支撑/阻力位以及识别出的交易机会等级（例如：'高确定性第一类买点'）。"
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
        if not result.tool_calls and result.content:
            report = result.content
        elif result.tool_calls:
            report = f"已调用工具 {', '.join([tc['name'] for tc in result.tool_calls])} 准备进行技术分析..."

        return {
            "messages": [result],
            "market_report": report, # 在原版中是 market_report
        }

    return market_analyst_node