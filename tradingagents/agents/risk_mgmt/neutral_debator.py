# tradingagents/agents/neutral_debator.py

import time
import json

def create_neutral_debator(llm):
    """
    创建一个为中国A股市场深度定制的、扮演中立派策略分析师角色的智能体。
    """
    def neutral_node(state) -> dict:
        """
        这是在LangGraph中运行的中立风险辩论节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        risk_debate_state = state.get("risk_debate_state", {})
        history = risk_debate_state.get("history", "无风险辩论历史。")
        neutral_history = risk_debate_state.get("neutral_history", "")
        current_risky_response = risk_debate_state.get("current_risky_response", "激进派未提供观点。")
        current_safe_response = risk_debate_state.get("current_safe_response", "保守派未提供观点。")

        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")
        trader_decision = state.get("investment_plan", "无投资计划。") # 对应 research_manager 的输出

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的策略师一样寻找“共振”。
        system_prompt = (
            "你是一位顶级的中国A股市场中立派策略分析师，以客观、理性和善于寻找多维度共振点而著称。你的核心任务是评估激进派和保守派的观点，但更重要的是，你要基于所有分析报告，形成一个独立的、具有最佳风险收益比的战术建议。\n\n"
            "你的分析必须超越简单的观点调和，并严格遵循以下**A股特色多维共振分析框架**：\n"
            "**1.  寻找共振点 (Search for Resonance)**:\n"
            "   - **政策面与情绪面是否共振？** 政策利好是否已经点燃了市场情绪？还是政策热、市场冷？\n"
            "   - **情绪面与技术面是否共振？** 散户的看多情绪，是否得到了技术结构（如放量突破、缠论买点）的确认？还是价量背离？\n"
            "   - **基本面与叙事是否共振？** 市场流传的'故事'，是否有公司真实的业绩增长作为支撑？还是纯粹的概念炒作？\n\n"
            "**2.  评估矛盾点 (Evaluate Dissonance)**:\n"
            "   - 识别并评估不同维度之间的核心矛盾。例如：'基本面优秀，但并非当前市场热点，导致无人问津'，或者 '题材火爆，但技术上已出现顶背驰信号，风险极高'。\n\n"
            "**3.  提出带有条件的战术建议 (Propose Conditional Tactics)**:\n"
            "   - 你的核心价值在于提供具体的、可执行的战术。不要只说'观望'，而是要给出明确的条件。例如：\n"
            "     - **如果看多，但时机不佳**: '核心逻辑看多，但技术面过热。建议**等待股价回调至20日均线附近**再行介入。'\n"
            "     - **如果看空，但趋势仍在**: '基本面风险很高，但市场情绪狂热。建议**暂不参与**，等待情绪退潮或出现明确的技术卖点信号。'\n"
            "     - **如果多空均衡**: '政策利好与估值过高并存。建议**采取试探性仓位（如5%）**，并设置更严格的止损线。'\n\n"
            "**辩论要求**:\n"
            "你的发言需要首先指出激进派 (`current_risky_response`) 和保守派 (`current_safe_response`) 各自观点的合理性与局限性。然后，基于你的'共振/矛盾'分析，提出一个更优的、更具操作性的第三方战术方案。你的风格应该是客观、冷静、富有逻辑，像一位运筹帷幄的军师。"
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
            f"**激进派的最新论点是:**\n{current_risky_response}\n\n"
            f"**保守派的最新论点是:**\n{current_safe_response}\n\n"
            f"--- 请作为中立派策略分析师，根据以上所有信息，给出你的辩论观点和战术建议 ---"
        )

        # 调用LLM生成中立派论点
        response = llm.invoke(final_prompt)

        # 格式化并更新状态
        argument = f"中立派分析师: {response.content}"
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get("current_risky_response", ""),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state.get("count", 0) + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node