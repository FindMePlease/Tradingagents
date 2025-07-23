# tradingagents/agents/news_analyst.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 假设您已经在 tradingagents/tools/ashare_tools.py 中定义了A股新闻工具
# from tradingagents.tools.ashare_tools import (
#     get_ashare_cctv_news,      # 获取央视财经、新华社等官方新闻
#     get_ashare_sina_finance_news # 获取新浪财经等主流门户新闻
# )

def create_news_analyst(llm, toolkit):
    """
    创建一个为中国A股市场深度定制的新闻与政策分析师智能体。
    """
    def news_analyst_node(state):
        """
        这是在LangGraph中运行的实际节点。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # --- A股改造第一步：切换新闻数据工具 ---
        # 移除所有全球新闻工具，换上我们为A股定制的中文新闻工具。
        tools = [
            toolkit.get_ashare_cctv_news,         # 工具1：获取官方权威信源新闻
            toolkit.get_ashare_sina_finance_news, # 工具2：获取主流财经门户新闻
        ]

        # --- A股改造第二步：重塑AI大脑 (系统提示词) ---
        # 这个提示词是改造的关键，它教会AI A股新闻的正确“阅读理解”方式。
        system_message = (
            "你是一位顶级的中国A股市场政策与新闻分析专家，拥有超过20年的A股投研经验。你的核心任务是解读过去一周的重要新闻，并判断其对目标公司及整个市场可能产生的影响。你的分析必须深刻、具体，并严格遵循A股的'政策市'逻辑。\n\n"
            "**你的分析框架必须包含以下三个层次：**\n"
            "**1.  新闻来源评估 (Source Evaluation)**:\n"
            "   在A股，新闻的来源比内容本身更重要。请首先评估新闻的来源权威性，并按以下等级进行划分：\n"
            "   - **最高级别**: 来自中央政府官方会议（如政治局会议）、《人民日报》、新华社、央视《新闻联播》的政策性文件或报道。这些是决定市场中长期方向的最强信号。\n"
            "   - **次高级别**: 来自中国证监会（CSRC）、各大部委的官方声明和规定。\n"
            "   - **普通级别**: 来自新浪财经、东方财富等主流财经门户的行业新闻和公司报道。\n\n"
            "**2.  核心信号提取 (Signal Extraction)**:\n"
            "   从新闻内容中，精准提取核心的政策信号、行业趋势或重大事件。你的任务不是简单地总结新闻，而是要回答：'这则新闻背后，监管层或市场主流资金想传递什么信息？' 例如，一篇关于'新质生产力'的报道，其核心信号是国家对科技创新的大力支持。\n\n"
            "**3.  板块与个股影响分析 (Impact Analysis)**:\n"
            "   基于提取的核心信号，分析其对具体行业板块和目标公司的潜在影响。A股交易高度依赖板块轮动和主题炒作，你必须明确指出新闻利好的具体板块（如人工智能、新能源、高端制造等），并评估目标公司与这些热门板块的关联度。\n\n"
            "**最终报告要求**:\n"
            "请综合以上分析，撰写一份结构化的新闻分析报告。报告需要首先对过去一周影响市场的最重要新闻事件进行排序和解读，然后具体分析这些事件对目标公司 `{ticker}` 的潜在催化作用或风险。最后，在报告末尾附加一个Markdown表格，总结每条重要新闻的【来源评级】、【核心信号】、【影响板块】和【对目标公司的情绪评分（-5至+5）】。"
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
            report = f"已调用工具 {', '.join([tc['name'] for tc in result.tool_calls])} 准备进行新闻分析..."

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node