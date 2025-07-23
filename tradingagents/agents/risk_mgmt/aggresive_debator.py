# tradingagents/agents/aggresive_debator.py

import time
import json

def create_risky_debator(llm):
    """
    创建一个为中国A股市场深度定制的、扮演激进派风险分析师（“游资”风格）的智能体。
    """
    def risky_node(state) -> dict:
        """
        这是在LangGraph中运行的激进风险辩论节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        risk_debate_state = state.get("risk_debate_state", {})
        history = risk_debate_state.get("history", "无风险辩论历史。")
        risky_history = risk_debate_state.get("risky_history", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "保守派未提供观点。")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "中立派未提供观点。")

        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        # 修复原代码中的一个笔误
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")
        trader_decision = state.get("investment_plan", "无投资计划。") # 对应 research_manager 的输出

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的顶尖“游资”一样思考风险与机会。
        system_prompt = (
            "你是一位顶尖的中国A股市场'游资'风格风险分析师，以嗅觉敏锐、决策果断、敢于拥抱不确定性而闻名。你的核心任务是支持基金经理的进攻性决策，并从'题材'和'资金'的角度，反驳保守派和中立派的过度谨慎。\n\n"
            "你的论证必须聚焦于**机会而非风险**，并严格遵循以下**A股特色激进论证框架**：\n"
            "**1.  题材与叙事就是最大的基本面 (Narrative is the new Fundamental)**:\n"
            "   - 深入挖掘新闻和情绪报告，寻找支持当前交易计划的**核心题材和市场叙事**。这个'故事'的想象空间有多大？是否是市场当前最关注的'主线'？在A股，一个强大的叙事可以暂时让传统的基本面和估值失效。\n\n"
            "**2.  资金共识大于一切 (Consensus Overrides Valuation)**:\n"
            "   - 寻找资金正在形成共识的证据。情绪报告中是否有'龙头'、'卡位'等关键词？技术报告中成交量是否异常放大？要强调，当市场形成共识时，追随资金流是最高效的策略，过度纠结于估值只会导致'踏空'。\n\n"
            "**3.  风险是收益的来源 (Risk is the Source of Alpha)**:\n"
            "   - 直接反驳保守派提出的风险点。例如，如果他们担忧'高波动性'，你的论点应该是'高波动性正是短线超额收益的来源'。如果他们担忧'基本面瑕疵'，你的论点应该是'市场当前交易的是预期和题材，而非历史财报'。\n\n"
            "**4.  机会的稀缺性 (Scarcity of Opportunity)**:\n"
            "   - 强调当前机会的稀缺性和稍纵即逝的特性。论证为什么现在是最佳的介入时机，犹豫和等待只会增加机会成本。\n\n"
            "**辩论要求**:\n"
            "你的发言必须充满激情和说服力，直接回应保守派 (`current_safe_response`) 和中立派 (`current_neutral_response`) 的每一个疑虑。你的目标不是否定风险的存在，而是论证**为什么潜在的回报值得去冒这些风险**。你的风格应该是果断、自信，展现出对市场机会的强大信念。"
        )

        # --- 准备输入给LLM的完整上下文 ---
        all_reports = (
            f"**基本面分析报告:**\n{fundamentals_report}\n\n"
            f"**技术分析报告:**\n{market_report}\n\n"
            f"**新闻与政策分析报告:**\n{news_report}\n\n"
            f"**社交媒体情绪报告:**\n{sentiment_report}"
        )

        final_prompt = (
            f"{system_prompt}\n\n"
            f"--- 以下是当前辩论的上下文 ---\n\n"
            f"**基金经理的初步投资计划是:**\n{trader_decision}\n\n"
            f"**分析师综合报告:**\n{all_reports}\n\n"
            f"**完整的风险辩论历史:**\n{history}\n\n"
            f"**保守派的最新论点是:**\n{current_safe_response}\n\n"
            f"**中立派的最新论点是:**\n{current_neutral_response}\n\n"
            f"--- 请作为激进派风险分析师，根据以上所有信息，给出你的辩论观点 ---"
        )

        # 调用LLM生成激进派论点
        response = llm.invoke(final_prompt)

        # 格式化并更新状态
        argument = f"激进派分析师: {response.content}"
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get("current_neutral_response", ""),
            "count": risk_debate_state.get("count", 0) + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node