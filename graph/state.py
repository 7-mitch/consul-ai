from typing import TypedDict, Annotated
import operator


class ConsultingState(TypedDict):
    """
    LangGraphが管理するエージェント間の共有State。
    各ノードはこのStateを受け取り、更新して返す。
    """
    # 入力
    client_input: str

    # 各エージェントの出力（順番にセットされていく）
    issue_analysis_result: str       # 課題分析Agentの出力
    roi_estimation_result: str       # ROI試算Agentの出力
    roadmap_result: str              # ロードマップAgentの出力
    final_proposal_result: str       # 提案書サマリーAgentの出力

    # メタ情報
    current_agent: str        # 現在実行中のエージェント名
    error: str                # エラーメッセージ（あれば）
