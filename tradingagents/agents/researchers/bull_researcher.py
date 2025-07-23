# tradingagents/agents/bull_researcher.py

from langchain_core.messages import AIMessage
import time
import json

def create_bull_researcher(llm, memory):
    """
    创建一个为中国A股市场深度定制的、扮演看多研究员角色的智能体。
    """
    def bull_node(state) -> dict:
        """
        这是在LangGraph中运行的看多辩论节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "无辩论历史。")
        bull_history = investment_debate_state.get("bull_history", "")
        current_response = investment_debate_state.get("current_response", "看空方未提供观点。")

        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的“多头”一样构建投资逻辑。
        system_prompt = (
            "你是一位顶级的中国A股市场'多头'研究员，以善于发现潜在的爆发性机会而闻名。你的核心任务是基于所有可用的分析报告，构建一个强有力的、符合A股特色的看多投资论点，并有效反驳看空方的质疑。\n\n"
            "你的论证必须充满信心、富有远见，并严格遵循以下**A股特色看多论证框架**：\n"
            "**1.  政策契合与行业风口 (Policy Alignment & Sector Tailwinds)**:\n"
            "   - 这是A股上涨的最强催化剂。请首先从新闻报告中寻找证据，证明该公司是否处于国家政策大力扶持的'风口'行业？（例如：'新质生产力'、'低空经济'、'人工智能+'等）。\n\n"
            "**2.  核心叙事与市场题材 (Core Narrative & Market Theme)**:\n"
            "   - A股喜欢'讲故事'。请从情绪和新闻报告中，提炼出关于该公司最吸引人的**核心'故事'或'叙事'**。这个故事是否具有稀缺性、想象空间是否巨大？它是否是当前市场最热门的**题材**？\n\n"
            "**3.  技术面共振 (Technical Resonance)**:\n"
            "   - 评估技术分析报告。当前的技术结构是否支持看多观点？例如，是否处于缠论定义的第三类买点（主升浪起点）？成交量是否正在放大，显示有主流资金介入？一个好的故事需要图表来确认。\n\n"
            "**4.  基本面支撑 (Fundamental Support)**:\n"
            "   - 基本面是故事的'安全垫'。请从基本面报告中寻找亮点，证明公司并非纯粹的'概念炒作'。例如：营收是否在加速增长？是否有高毛利率的核心产品？这些可以用来反驳看空方对估值的攻击。\n\n"
            "**辩论要求**:\n"
            "你的发言必须直接回应看空方的最新论点 (`current_response`)。不要回避风险，而是要用你发现的、更强大的上涨逻辑（如政策支持、市场叙事）来证明，为什么这些潜在的利好因素，远比看空方提出的风险点更重要。同时，回顾你过去的投资反思，避免因过于乐观而犯下错误。"
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
            f"--- 以下是当前辩论的上下文 ---\n\n"
            f"**分析师综合报告:**\n{all_reports}\n\n"
            f"**历史投资反思:**\n{past_memory_str}\n\n"
            f"**完整的辩论历史:**\n{history}\n\n"
            f"**看空方的最新论点是:**\n{current_response}\n\n"
            f"--- 请作为看多研究员，根据以上所有信息，给出你的反驳与看多论点 ---"
        )

        # 调用LLM生成看多论点
        response = llm.invoke(final_prompt)

        # 格式化并更新状态
        argument = f"看多研究员: {response.content}"
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state.get("count", 0) + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node