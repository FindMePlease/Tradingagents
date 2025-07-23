# tradingagents/utils/memory.py

import chromadb
from chromadb.config import Settings
from openai import OpenAI
import json
from typing import List, Dict, Tuple

class AshareMemoryManager:
    """
    一个为中国A股市场深度定制的、结构化的长期记忆与交易复盘系统。
    它取代了原版简单的文本拼接，使用结构化的“市场快照”和“交易复盘档案”来提升记忆的质量和检索的精准度。
    """
    def __init__(self, name: str, config: Dict):
        # 优化：优先选择针对中文优化的嵌入模型
        # 如果使用本地模型（如Ollama），可以指定中文特化模型
        if config.get("backend_url") and "localhost" in config["backend_url"]:
            self.embedding_model = "nomic-embed-text" # 示例，可替换为其他本地中文模型
        else:
            # OpenAI的text-embedding-3-small对多语言支持很好，是一个不错的选择
            self.embedding_model = "text-embedding-3-small"
            
        self.client = OpenAI(base_url=config.get("backend_url"))
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.collection = self.chroma_client.create_collection(name=name)
        print(f"A股记忆模块 '{name}' 初始化成功，使用嵌入模型: {self.embedding_model}")

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量"""
        response = self.client.embeddings.create(
            model=self.embedding_model, input=text
        )
        # 注意：根据OpenAI最新API版本，访问方式可能为 response.data.embedding
        # 请根据您使用的openai库版本确认
        return response.data.embedding

    def _create_structured_snapshot(self, state: Dict) -> str:
        """
        A股改造核心1：创建结构化的市场快照，而不是简单的文本拼接。
        这能生成更高质量、信息更密集的嵌入向量。
        """
        snapshot = {
            "policy_signal": f"新闻政策分析的核心观点: {state.get('news_report', '无')[:100]}...",
            "sentiment_stage": f"市场情绪分析的核心观点: {state.get('sentiment_report', '无')[:100]}...",
            "technical_structure": f"技术结构分析的核心观点: {state.get('market_report', '无')[:100]}...",
            "fundamental_risk": f"基本面分析的核心风险: {state.get('fundamentals_report', '无')[:100]}..."
        }
        return (
            f"### 市场快照\n"
            f"- **政策信号**: {snapshot['policy_signal']}\n"
            f"- **情绪阶段**: {snapshot['sentiment_stage']}\n"
            f"- **技术结构**: {snapshot['technical_structure']}\n"
            f"- **基本面风险**: {snapshot['fundamental_risk']}"
        )

    def add_trade_memory(self, state: Dict, trade_outcome: Dict):
        """
        A股改造核心2：添加一笔完整的交易记忆，包含情景、决策和最终结果。
        
        :param state: 交易决策时的完整状态 (state)
        :param trade_outcome: 交易结束后的结果，例如 {'outcome': '+5.2%', 'lesson': '政策利好与情绪共振，但入场点位过高导致利润回吐。'}
        """
        situation_snapshot = self._create_structured_snapshot(state)
        
        trade_case_study = {
            "investment_plan": state.get("investment_plan", "无"),
            "trade_outcome": trade_outcome.get("outcome", "未知"),
            "key_lesson": trade_outcome.get("lesson", "无经验总结")
        }

        doc_id = str(self.collection.count())
        embedding = self._get_embedding(situation_snapshot)
        
        self.collection.add(
            documents=[situation_snapshot],
            metadatas=[{"case_study": json.dumps(trade_case_study, ensure_ascii=False)}],
            embeddings=[embedding],
            ids=[doc_id],
        )
        print(f"成功添加一条A股交易记忆，ID: {doc_id}")

    def get_similar_memories(self, current_state: Dict, n_matches: int = 2) -> List:
        """
        根据当前市场情况，检索最相似的历史交易复盘档案。
        """
        current_snapshot = self._create_structured_snapshot(current_state)
        query_embedding = self._get_embedding(current_snapshot)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        # --- 优化点 1: 修复语法错误 ---
        matched_results = 
        
        # --- 优化点 2: 增强健壮性，检查查询结果是否有效 ---
        if not results or not results["documents"] or not results["documents"]:
            return matched_results # 如果没有找到任何匹配项，返回空列表

        # --- 优化点 3: 修复数据访问逻辑 ---
        # ChromaDB返回的结果是嵌套列表，需要用  来访问第一层
        for i in range(len(results["documents"])):
            case_study_json = results["metadatas"][i].get("case_study", "{}")
            matched_results.append({
                "matched_situation": results["documents"][i],
                "case_study": json.loads(case_study_json),
                "similarity_score": 1 - results["distances"][i],
            })
        return matched_results