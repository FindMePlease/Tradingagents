# tradingagents/agents/social_media_analyst.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 假设您已经在 tradingagents/tools/ashare_tools.py 中定义了A股社区数据工具
# from tradingagents.tools.ashare_tools import (
#     get_guba_discussions,         # 获取东方财富/同花顺股吧的热门帖子
#     get_xueqiu_discussions,      # 获取雪球社区的深度讨论
#     get_weibo_financial_posts,   # 获取微博财经大V和相关话题的帖子
#     get_douyin_video_transcripts # 获取抖音财经视频的文本内容和评论（高级功能）
# )

def create_social_media_analyst(llm, toolkit):
    """
    创建一个为中国A股市场深度定制的、多源社交媒体与情绪分析师智能体。
    """
    def social_media_analyst_node(state):
        """
        这是在LangGraph中运行的实际节点。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # --- A股改造第一步：构建本土化的社交媒体工具矩阵 ---
        # 移除Reddit工具，换上覆盖中国主流投资者社区的工具集。
        tools = [
            toolkit.get_guba_discussions,         # 工具1: 股吧 - 捕捉最广泛的散户情绪
            toolkit.get_xueqiu_discussions,       # 工具2: 雪球 - 捕捉深度逻辑和“聪明散户”观点
            toolkit.get_weibo_financial_posts,    # 工具3: 微博 - 追踪财经大V影响力
            toolkit.get_douyin_video_transcripts  # 工具4: 抖音 - 捕捉新兴舆论场（技术实现较复杂）
        ]

        # --- A股改造第二步：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI如何从多个维度理解A股的舆论生态。
        system_message = (
            "你是一位顶级的中国A股市场舆情分析专家，对同花顺、雪球、微博、抖音等平台的语言风格和情绪动态有深刻的洞察。你的核心任务是综合分析过去一周关于目标公司的多平台舆论，并为交易员提供一份关于当前市场情绪、主流叙事和潜在催化剂的深度分析报告。\n\n"
            "你的分析必须超越简单的正面/负面判断，并严格遵循以下A股特色的**四维舆情分析框架**：\n"
            "**1.  主流情绪诊断 (Overall Sentiment Diagnosis)**:\n"
            "   综合所有平台信息，判断当前市场对该股票的主流情绪是**看涨 (Bullish)**、**看跌 (Bearish)**，还是**分歧/迷茫 (Disagreement/Confused)**。并评估情绪的强度。\n\n"
            "**2.  核心叙事与题材挖掘 (Narrative & Theme Mining)**:\n"
            "   这是A股分析的精髓。请识别当前市场正在流传的、关于该公司的核心**'故事'或'叙事' (Narrative)**。这个故事是否与当前最热门的**市场题材 (Theme)** 相关联？（例如：'该公司被挖掘出是“低空经济”概念的隐藏龙头'，'其AI芯片被认为是“新质生产力”的关键一环'）。\n\n"
            "**3.  关键意见领袖(KOL)影响力评估 (KOL Impact Assessment)**:\n"
            "   识别是否有知名的财经'大V'或影响力人物（在微博、雪球或抖音上）正在讨论该公司。他们的观点是什么？他们的观点是否正在被大量散户跟随和传播？\n\n"
            "**4.  舆情热度与阶段判断 (Hype Level & Stage Assessment)**:\n"
            "   评估当前舆情的**热度**（讨论量是温和、火爆还是现象级？）。并判断舆情发酵处于哪个阶段：是**早期发酵 (Brewing)**，**快速扩散 (Accelerating)**，**全面高潮 (Climax/Euphoria)**，还是**热度退潮 (Fading)**？\n\n"
            "**最终报告要求**:\n"
            "请综合以上四点，撰写一份结构化的舆情分析报告。报告需要逻辑清晰，有理有据。最后，在报告末尾附加一个Markdown表格，总结你的核心发现，包含【主流情绪】、【核心叙事/题材】、【关键KOL观点】和【舆情热度与阶段】。"
        )

        # --- 以下为LangChain和LangGraph的标准流程 ---
        prompt = ChatPromptTemplate.from_messages(
            
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if not result.tool_calls and result.content:
            report = result.content
        elif result.tool_calls:
            report = f"已调用工具 {', '.join([tc['name'] for tc in result.tool_calls])} 准备进行社交媒体分析..."

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node