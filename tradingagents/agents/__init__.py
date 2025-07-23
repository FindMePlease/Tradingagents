# tradingagents/__init__.py

# --- A股改造核心：导入我们为A股市场定制的核心模块 ---

# 1. 从 utils 包中，导入我们全新的A股工具箱、结构化状态和记忆管理器
from.utils.agent_utils import AshareToolkit, create_msg_delete
from.utils.agent_states import (
    AgentState, 
    InvestDebateState, 
    RiskDebateState,
    TradeInstruction,  # 导入结构化的交易指令
    RiskAssessment     # 导入结构化的风险评估
)
from.utils.memory import AshareMemoryManager

# 2. 导入所有经过A股本地化改造的智能体创建函数
#    这些文件的内部逻辑（提示词）已经被我们优化，但函数名保持不变，便于接入主工作流
from.analysts.fundamentals_analyst import create_fundamentals_analyst
from.analysts.market_analyst import create_market_analyst
from.analysts.news_analyst import create_news_analyst
from.analysts.social_media_analyst import create_social_media_analyst

from.researchers.bear_researcher import create_bear_researcher
from.researchers.bull_researcher import create_bull_researcher

from.risk_mgmt.aggresive_debator import create_risky_debator
from.risk_mgmt.conservative_debator import create_safe_debator
from.risk_mgmt.neutral_debator import create_neutral_debator

from.managers.research_manager import create_research_manager
from.managers.risk_manager import create_risk_manager

from.trader.trader import create_trader

# --- A股改造核心：更新软件包的“公开产品目录” (__all__) ---
# 这个列表定义了当其他脚本从本包导入时，哪些名称是公开可用的。
# 我们将原有的类替换为我们A股定制版的新类，并补全了列表。
__all__ = [
    "AshareToolkit",
    "create_msg_delete",
    "AgentState",
    "InvestDebateState",
    "RiskDebateState",
    "TradeInstruction",
    "RiskAssessment",
    "AshareMemoryManager",
    "create_fundamentals_analyst",
    "create_market_analyst",
    "create_news_analyst",
    "create_social_media_analyst",
    "create_bear_researcher",
    "create_bull_researcher",
    "create_risky_debator",
    "create_safe_debator",
    "create_neutral_debator",
    "create_research_manager",
    "create_risk_manager",
    "create_trader"
]