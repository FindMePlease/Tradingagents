# tradingagents/utils/agent_states.py

from typing import Annotated, Sequence, Dict, Any
from datetime import date
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

# --- A股改造第一步：为关键决策定义结构化的数据类型 ---

class TradeInstruction(TypedDict):
    """
    定义由'首席交易员' (trader) 生成的、完全结构化的交易指令。
    这取代了原版模糊的自然语言计划。
    """
    action: Annotated
    ticker: Annotated
    position_size: Annotated[float, "仓位百分比，范围0到1.0"]
    order_type: Annotated
    reasoning: Annotated[str, "制定此交易指令的核心理由"]

class RiskAssessment(TypedDict):
    """
    定义由'首席风险官' (risk_manager) 生成的、完全结构化的风险评估报告。
    这取代了原版模糊的自然语言决策。
    """
    approval: Annotated
    risk_score: Annotated[int, "综合风险评分，从1到10"]
    adjustments: Annotated[str, "具体的调整建议，例如 '将建议仓位从20%下调至10%'"]
    reasoning: Annotated[str, "做出此风险评估的核心理由"]


# --- 以下为对原版状态对象的优化和适配 ---

class InvestDebateState(TypedDict):
    """研究员团队（牛熊辩论）的状态"""
    bull_history: str
    bear_history: str
    history: str
    current_response: str
    judge_decision: str
    count: int

class RiskDebateState(TypedDict):
    """风险管理团队辩论的状态"""
    risky_history: str
    safe_history: str
    neutral_history: str
    history: str
    latest_speaker: str
    current_risky_response: str
    current_safe_response: str
    current_neutral_response: str
    judge_decision: str # 这里可以保留为自然语言，因为最终决策在 final_trade_decision 中
    count: int

# 继承自 LangGraph 的基础状态，通常包含一个 messages 列表
class BaseAgentState(TypedDict):
    messages: Annotated, "对话消息序列"]

class AgentState(BaseAgentState):
    """
    整个A股TradingAgents工作流的全局状态。
    """
    # --- 基础输入信息 ---
    company_of_interest: str
    trade_date: str
    sender: str # 记录最新消息的发送者

    # --- 分析师团队报告 ---
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str

    # --- 研究员团队（基金经理）决策 ---
    investment_debate_state: InvestDebateState
    investment_plan: str # 基金经理的宏观投资计划，保留为自然语言

    # --- 交易员决策 ---
    # 优化：用结构化的 TradeInstruction 取代原版的 trader_investment_plan 字符串
    trade_instruction: TradeInstruction 

    # --- 风险管理团队决策 ---
    risk_debate_state: RiskDebateState
    # 优化：用结构化的 RiskAssessment 取代原版的 final_trade_decision 字符串
    final_risk_assessment: RiskAssessment