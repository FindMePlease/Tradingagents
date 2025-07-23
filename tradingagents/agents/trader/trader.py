# tradingagents/agents/trader.py

import functools
import time
import json

def create_trader(llm, memory):
    """
    创建一个为中国A股市场深度定制的、扮演首席交易员角色的智能体。
    """
    def trader_node(state, name):
        """
        这是在LangGraph中运行的交易员决策节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        company_name = state.get("company_of_interest", "未知公司")
        investment_plan = state.get("investment_plan", "无投资计划。")
        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的专业交易员一样思考执行细节。
        system_prompt = (
            "你是一位顶级的中国A股市场首席交易员，以执行精准、纪律严明著称。你的核心任务是解读基金经理下达的投资计划，并将其转化为一份具体的、可立即执行的、结构化的交易指令。\n\n"
            "你的决策必须充分考虑A股市场的微观交易结构和规则，并遵循以下**A股特色交易执行框架**：\n"
            "**1.  决策转换 (Plan to Action)**:\n"
            "   - 首先，明确基金经理投资计划的核心意图是**买入 (BUY)**、**卖出 (SELL)**，还是**持有 (HOLD)**。\n\n"
            "**2.  仓位管理 (Position Sizing)**:\n"
            "   - 基于投资计划中的信心和理由，决定本次操作的**仓位大小**。使用投资组合总资产的百分比来表示（例如：'10%'代表使用10%的资金建仓）。对于高风险的题材股，仓位应更谨慎；对于高确定性的机会，仓位可适当提高。\n\n"
            "**3.  订单策略 (Order Strategy)**:\n"
            "   - 决定最佳的订单类型。对于流动性好的大盘股，可以使用**市价单 (Market Order)** 以确保成交。对于波动大、流动性一般的中小盘股，为控制成本，应优先考虑使用**限价单 (Limit Order)**，并给出一个合理的报价范围（例如：'在当前价±0.5%的范围内下单'）。\n\n"
            "**4.  执行时机考量 (Timing Consideration)**:\n"
            "   - 结合A股T+1规则和日内流动性特征，思考最佳的执行时间。例如，对于卖出操作，要避免在早盘的恐慌性抛压中卖出；对于买入操作，要避免在午后的情绪高点追高。\n\n"
            "**最终输出要求**:\n"
            "你的最终输出**必须是一个严格的JSON格式字符串**，以便于程序解析和自动化执行。JSON中必须包含以下字段：\n"
            "- `action` (字符串): 必须是 'BUY', 'SELL', 'HOLD' 之一。\n"
            "- `ticker` (字符串): 目标股票代码。\n"
            "- `position_size` (浮点数): 仓位百分比，范围0到1.0。如果是HOLD或SELL，此项可为0。\n"
            "- `order_type` (字符串): 'MARKET' 或 'LIMIT'。\n"
            "- `reasoning` (字符串): 简明扼要地陈述你制定此交易指令的核心理由。\n\n"
            "**示例输出**:\n"
            "```json\n"
            "{\n"
            "  \"action\": \"BUY\",\n"
            "  \"ticker\": \"600519.SH\",\n"
            "  \"position_size\": 0.15,\n"
            "  \"order_type\": \"LIMIT\",\n"
            "  \"reasoning\": \"基金经理看多，政策面和情绪面形成共振。技术面处于突破位置，为控制成本采用限价单方式建仓15%。\"\n"
            "}\n"
            "```"
        )

        # --- 准备输入给LLM的完整上下文 ---
        all_reports = (
            f"**基本面分析报告:**\n{fundamentals_report}\n\n"
            f"**技术分析报告:**\n{market_report}\n\n"
            f"**新闻与政策分析报告:**\n{news_report}\n\n"
            f"**社交媒体情绪报告:**\n{sentiment_report}"
        )
        
        past_memories = memory.get_memories(all_reports, n_matches=2)
        past_memory_str = "\n".join([f"- {rec['recommendation']}" for rec in past_memories]) if past_memories else "无相关的历史经验可供参考。"

        final_prompt = (
            f"{system_prompt}\n\n"
            f"--- 以下是待执行的投资计划和相关信息 ---\n\n"
            f"**公司名称:** {company_name} ({ticker})\n\n"
            f"**基金经理的投资计划:**\n{investment_plan}\n\n"
            f"**历史交易反思:**\n{past_memory_str}\n\n"
            f"**分析师综合报告:**\n{all_reports}\n\n"
            f"--- 请作为首席交易员，根据以上所有信息，生成你的最终交易指令（必须为JSON格式） ---"
        )

        # 调用LLM生成交易指令
        result = llm.invoke(final_prompt)

        return {
            "messages": [result],
            "trader_investment_plan": result.content, # 保持原有的键名，但内容已是结构化的JSON
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")