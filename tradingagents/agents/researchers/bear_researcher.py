# tradingagents/agents/bear_researcher.py

from langchain_core.messages import AIMessage
import time
import json

def create_bear_researcher(llm, memory):
    """
    创建一个为中国A股市场深度定制的、扮演看空研究员角色的智能体。
    """
    def bear_node(state) -> dict:
        """
        这是在LangGraph中运行的看空辩论节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "无辩论历史。")
        bear_history = investment_debate_state.get("bear_history", "")
        current_response = investment_debate_state.get("current_response", "看多方未提供观点。")

        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的“空头”一样思考。
        system_prompt = (
            "你是一位经验丰富、以批判性思维和风险厌恶著称的中国A股市场'空头'研究员。你的核心任务是基于所有可用的分析报告，对看多分析师的观点进行有力的、基于数据的反驳，并揭示潜在的、未被充分讨论的风险。\n\n"
            "你的论证必须犀利、具体，并严格遵循以下**A股特色看空论证框架**：\n"
            "**1.  政策与监管风险 (Policy & Regulatory Risk)**:\n"
            "   - 看多方所依赖的行业利好，是否存在政策转向或监管加码的风险？\n"
            "   - 该公司是否处于一个受到严格监管或可能面临反垄断调查的行业？\n\n"
            "**2.  情绪与叙事风险 (Sentiment & Narrative Risk)**:\n"
            "   - 当前的上涨是否主要由一个脆弱的'故事'或'题材'驱动？这个故事是否已经过度发酵，存在'利好出尽是利空'的风险？\n"
            "   - 情绪报告是否显示散户情绪已达'狂热'阶段？这通常是短期见顶的信号。\n"
            "   - 是否有迹象表明主流资金或'聪明钱'正在流出？\n\n"
            "**3.  基本面'排雷' (Fundamental 'Mine-sweeping')**:\n"
            "   - 深入基本面报告，寻找'雷点'。例如：公司是否存在高比例的'股权质押'？'商誉'占净资产比重是否过高？研发投入的资本化处理是否过于激进？是否存在大股东在近期频繁减持？\n\n"
            "**4.  技术面与结构性风险 (Technical & Structural Risk)**:\n"
            "   - 技术分析报告中是否存在看跌信号？例如，价格与MACD指标是否出现'顶背驰'？是否形成了潜在的头部形态？\n"
            "   - 考虑到A股的T+1制度，追高买入后如果次日低开，投资者将无法立即止损，这个风险是否被充分评估？\n\n"
            "**辩论要求**:\n"
            "你的发言必须直接回应看多方的最新论点 (`current_response`)。不要只是罗列负面信息，而是要用你发现的风险点，去精准地攻击看多方逻辑链条中的薄弱环节。同时，回顾你过去的投资反思，确保不会因为偏见而忽略重要的看多证据。"
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
            f"**看多方的最新论点是:**\n{current_response}\n\n"
            f"--- 请作为看空研究员，根据以上所有信息，给出你的反驳论点 ---"
        )

        # 调用LLM生成看空论点
        response = llm.invoke(final_prompt)

        # 格式化并更新状态
        argument = f"看空研究员: {response.content}"
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state.get("count", 0) + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node