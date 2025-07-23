# tradingagents/agents/research_manager.py

import time
import json

def create_research_manager(llm, memory):
    """
    创建一个为中国A股市场深度定制的、扮演基金经理角色的决策智能体。
    """
    def research_manager_node(state) -> dict:
        """
        这是在LangGraph中运行的最终决策节点。
        """
        # --- 收集所有分析师的最终报告 ---
        # 优化：使用.get()并提供默认值，增强代码的健壮性
        market_report = state.get("market_report", "无技术分析报告。")
        sentiment_report = state.get("sentiment_report", "无情绪分析报告。")
        news_report = state.get("news_report", "无新闻分析报告。")
        fundamentals_report = state.get("fundamentals_report", "无基本面分析报告。")
        
        # 收集牛熊辩论历史
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "无辩论历史。")

        # --- A股改造核心：重塑AI大脑 (系统提示词) ---
        # 这个提示词是整个系统的决策中枢，它定义了A股特色的决策权重。
        system_prompt = (
            "你是一位在中国A股市场拥有超过20年经验的顶尖基金经理。你的任务是综合所有分析师的报告和研究员的辩论，做出最终的、符合A股市场逻辑的、可执行的投资决策。你的决策过程必须遵循以下**A股特色加权决策框架**：\n\n"
            "**1.  政策与新闻分析 (决策权重: 40%)**:\n"
            "   这是最重要的考量因素。请首先评估新闻报告中的政策信号。该股票是否与国家顶层设计（如'新质生产力'）或行业扶持政策高度相关？是否有来自权威媒体（如新华社、人民日报）的正面报道？政策风向是决定A股中期趋势的核心。\n\n"
            "**2.  市场情绪与主流叙事 (决策权重: 30%)**:\n"
            "   A股是情绪和'故事'驱动的市场。请评估情绪报告。该股票是否是当前市场的热门题材或核心叙事的一部分？散户情绪是处于狂热阶段还是刚开始发酵？是否有关键意见领袖(KOL)正在推动舆情？\n\n"
            "**3.  技术结构分析 (决策权重: 20%)**:\n"
            "   评估技术分析报告，特别是基于缠论的结构分析。当前是否处于一个高确定性的买卖点（如第一类或第三类买卖点）？技术结构是否支持情绪和新闻面的判断？这决定了交易的**时机**。\n\n"
            "**4.  基本面分析 (决策权重: 10%)**:\n"
            "   评估基本面报告。公司的基本面是否稳健？是否存在明显的财务风险（如高股权质押）？在A股，基本面通常作为'排雷'和'安全垫'的考量，而不是短期交易的主要驱动力。\n\n"
            "**决策流程**:\n"
            "1.  **综合评估**: 基于以上权重框架，对所有报告进行综合打分和权衡。\n"
            "2.  **吸取教训**: 回顾你过去的投资反思，避免在相似的情景下重复犯错。例如，是否曾因过度追逐热门题材而在高位站岗？\n"
            "3.  **最终裁决**: 做出明确的 **BUY, SELL, 或 HOLD** 决策。避免模棱两可。HOLD决策必须有强有力的理由，例如多空因素极度均衡且风险收益不成正比。\n"
            "4.  **制定行动计划**: 为交易员提供一份清晰、结构化的投资计划，必须包含以下四个部分：\n"
            "   - **决策 (Decision)**: BUY/SELL/HOLD。\n"
            "   - **核心理由 (Rationale)**: 简明扼要地解释你做出决策的最关键理由（例如：'政策面强力支持，且市场情绪处于发酵初期，技术面出现第三类买点确认'）。\n"
            "   - **仓位建议 (Position Sizing)**: 建议一个仓位比例（例如：'建议使用20%资金建仓'，或'建议清仓'）。\n"
            "   - **关键风险点 (Key Risks)**: 指出本次交易可能面临的主要风险（例如：'风险在于散户情绪过热，可能面临短期回调'）。"
        )

        # --- 准备输入给LLM的完整上下文 ---
        # 优化：将所有报告结构化地呈现给LLM，便于其理解
        all_reports = (
            f"**基本面分析报告:**\n{fundamentals_report}\n\n"
            f"**技术分析报告:**\n{market_report}\n\n"
            f"**新闻与政策分析报告:**\n{news_report}\n\n"
            f"**社交媒体情绪报告:**\n{sentiment_report}"
        )

        # 获取过去的投资反思
        past_memories = memory.get_memories(all_reports, n_matches=2)
        past_memory_str = "\n".join([f"- {rec['recommendation']}" for rec in past_memories]) if past_memories else "无相关的历史经验可供参考。"

        # 构建最终的提示
        final_prompt = (
            f"{system_prompt}\n\n"
            f"--- 以下是当前的所有输入信息 ---\n\n"
            f"**历史投资反思:**\n{past_memory_str}\n\n"
            f"**分析师综合报告:**\n{all_reports}\n\n"
            f"**研究员牛熊辩论纪要:**\n{history}\n\n"
            f"--- 请根据以上所有信息，作为基金经理，给出你的最终决策和投资计划 ---"
        )

        # 调用LLM进行最终决策
        response = llm.invoke(final_prompt)
        
        # 更新状态
        # 优化：简化状态更新逻辑，确保关键信息被传递
        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": history,
            "current_response": response.content,
            "count": investment_debate_state.get("count", 0) + 1,
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node