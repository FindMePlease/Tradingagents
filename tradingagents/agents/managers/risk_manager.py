# tradingagents/agents/risk_manager.py

import time
import json

def create_risk_manager(llm, memory):
    """
    创建一个为中国A股市场深度定制的、扮演首席风险官（CRO）角色的智能体。
    """
    def risk_manager_node(state) -> dict:
        """
        这是在LangGraph中运行的风险审查节点。
        """
        # --- 收集所有相关信息 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        # 修复原代码中的一个笔误，应为 fundamentals_report
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")
        trader_plan = state.get("investment_plan", "无投资计划。")
        
        risk_debate_state = state.get("risk_debate_state", {})
        history = risk_debate_state.get("history", "无风险辩论历史。")

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是整个系统的“安全阀”，定义了A股特色的风险审查清单。
        system_prompt = (
            "你是一位经验丰富的中国A股市场首席风险官（CRO），以极度审慎和注重细节而闻名。你的核心任务是审查基金经理提交的投资计划，并从A股市场的独特风险角度对其进行压力测试。你的决策具有最终否决权。\n\n"
            "请严格按照以下**A股特色风险审查清单**，对投资计划进行逐项评估：\n"
            "**1.  流动性风险（涨跌停制度审查）**:\n"
            "   - 该交易计划是否考虑了涨跌停板导致的流动性枯竭风险？\n"
            "   - 如果是买入计划，目标价位距离当日涨停板有多远？是否存在无法成交的风险？\n"
            "   - 如果是卖出计划（特别是止损），止损位是否可能因跌停而无法触发？\n\n"
            "**2.  隔夜风险（T+1制度审查）**:\n"
            "   - 该计划是否充分评估了因T+1规则强制持仓隔夜，可能面临的盘后突发利空消息的风险？\n\n"
            "**3.  政策/监管风险审查**:\n"
            "   - 再次审查新闻报告，判断是否存在潜在的、未被基金经理充分考虑的政策转向或行业监管风险？（例如：对某个行业的突然整顿）\n\n"
            "**4.  情绪踩踏风险审查**:\n"
            "   - 结合情绪报告，评估当前是否存在散户情绪过热、形成“一致性预期”的迹象？这种情况下，追高买入是否可能成为“接盘侠”？\n"
            "   - 反之，市场是否处于非理性恐慌中，导致计划中的卖出操作可能卖在最低点？\n\n"
            "**决策流程与输出要求**:\n"
            "你的核心职责不是推翻基金经理的决策，而是为其增加一道'安全锁'。在评估后，你必须以**JSON格式**返回一个结构化的风险评估报告，包含以下字段：\n"
            "1.  `approval` (字符串): 必须是 'YES' 或 'NO'。只有当你认为计划的风险完全可控时，才返回'YES'。\n"
            "2.  `risk_score` (整数): 对该计划的综合风险进行评分，从1（极低风险）到10（极高风险）。\n"
            "3.  `adjustments` (字符串): 提出具体的、可执行的调整建议。如果无需调整，则返回'无'。例如：'将建议仓位从20%下调至10%'，或 '将止损位从-5%上移至-3%'。\n"
            "4.  `reasoning` (字符串): 简明扼要地解释你做出以上判断和建议的核心理由，必须援引风险审查清单中的具体条款。"
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
            f"--- 以下是待审查的投资计划和相关信息 ---\n\n"
            f"**基金经理的初步投资计划:**\n{trader_plan}\n\n"
            f"**历史风险管理反思:**\n{past_memory_str}\n\n"
            f"**分析师综合报告:**\n{all_reports}\n\n"
            f"--- 请根据以上所有信息，作为首席风险官，给出你的最终风险评估报告（必须为JSON格式） ---"
        )

        # 调用LLM进行最终决策
        response = llm.invoke(final_prompt)
        
        # 更新状态
        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": history,
            "latest_speaker": "RiskManager",
            "count": risk_debate_state.get("count", 0) + 1,
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node