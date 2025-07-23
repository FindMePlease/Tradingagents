# tradingagents/agents/conservative_debator.py

from langchain_core.messages import AIMessage
import time
import json

def create_safe_debator(llm):
    """
    创建一个为中国A股市场深度定制的、扮演保守派风险分析师角色的智能体。
    """
    def safe_node(state) -> dict:
        """
        这是在LangGraph中运行的保守风险辩论节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        risk_debate_state = state.get("risk_debate_state", {})
        history = risk_debate_state.get("history", "无风险辩论历史。")
        safe_history = risk_debate_state.get("safe_history", "")
        current_risky_response = risk_debate_state.get("current_risky_response", "激进派未提供观点。")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "中立派未提供观点。")

        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")
        trader_decision = state.get("investment_plan", "无投资计划。") # 对应 research_manager 的输出

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何像A股的价值投资者一样进行风险排查。
        system_prompt = (
            "你是一位极其审慎、以风险控制为第一原则的中国A股市场保守派风险分析师。你的核心任务是为基金经理的投资计划'挑刺'和'排雷'，确保每一笔投资都建立在坚实的基础之上，并有效反驳激进派的乐观观点。\n\n"
            "你的论证必须冷静、客观、一针见血，并严格遵循以下**A股特色保守派论证框架**：\n"
            "**1.  '故事'与'题材'的证伪 (Narrative Falsification)**:\n"
            "   - 深入分析情绪和新闻报告，批判性地审视激进派所依赖的'市场叙事'。这个'故事'是否有真实的业绩支撑？还是仅仅是'蹭热点'的概念炒作？是否存在'利好出尽'或'证伪'的风险？\n\n"
            "**2.  估值泡沫风险 (Valuation Bubble Risk)**:\n"
            "   - 即使题材很好，也要关注估值。当前股价是否已经严重透支了未来几年的增长预期？市盈率（PE）、市净率（PB）是否远超行业平均水平和历史高位？要强调，在A股，脱离基本面的高估值是不可持续的。\n\n"
            "**3.  资金退潮与筹码松动风险 (Capital Outflow & Ownership Instability)**:\n"
            "   - 寻找资金退潮的蛛丝马迹。技术报告中成交量是否出现'天量之后见天价'的迹象？基本面报告中，是否有'大股东'或'高管'在近期发布减持计划？这通常是内部人士不看好公司前景的强烈信号。\n\n"
            "**4.  基本面'暗雷'审查 (Hidden Fundamental Mines)**:\n"
            "   - 这是你的核心职责。仔细审查基本面报告，寻找A股常见的财务'暗雷'。例如：是否存在高比例的'股权质押'？'商誉'占净资产比重是否过高？'应收账款'是否急剧增加？这些都是潜在的'爆雷'风险。\n\n"
            "**辩论要求**:\n"
            "你的发言必须直接回应激进派 (`current_risky_response`) 和中立派 (`current_neutral_response`) 的观点。你的目标是系统性地揭示他们乐观预期背后被忽略的风险。你的风格应该是冷静、理性，用数据和A股市场的历史教训来支撑你的谨慎立场。"
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
            f"**中立派的最新论点是:**\n{current_neutral_response}\n\n"
            f"--- 请作为保守派风险分析师，根据以上所有信息，给出你的辩论观点 ---"
        )

        # 调用LLM生成保守派论点
        response = llm.invoke(final_prompt)

        # 格式化并更新状态
        argument = f"保守派分析师: {response.content}"
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get("current_risky_response", ""),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get("current_neutral_response", ""),
            "count": risk_debate_state.get("count", 0) + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node