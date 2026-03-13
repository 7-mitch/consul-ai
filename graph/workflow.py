from langgraph.graph import StateGraph, END
from graph.state import ConsultingState
from graph.nodes import (
    issue_analysis_node,
    roi_estimation_node,
    roadmap_node,
    final_proposal_node,
)


def build_graph() -> StateGraph:
    """
    4エージェントの直列オーケストレーショングラフを構築する。

    フロー:
        issue_analysis
            ↓
        roi_estimation
            ↓
        roadmap
            ↓
        final_proposal
            ↓
           END
    """
    workflow = StateGraph(ConsultingState)

    # ノードを登録
    workflow.add_node("issue_analysis", issue_analysis_node)
    workflow.add_node("roi_estimation", roi_estimation_node)
    workflow.add_node("roadmap", roadmap_node)
    workflow.add_node("final_proposal", final_proposal_node)

    # エントリーポイント
    workflow.set_entry_point("issue_analysis")

    # エッジ（直列チェーン）
    workflow.add_edge("issue_analysis", "roi_estimation")
    workflow.add_edge("roi_estimation", "roadmap")
    workflow.add_edge("roadmap", "final_proposal")
    workflow.add_edge("final_proposal", END)

    return workflow.compile()


# グラフのシングルトン
consulting_graph = build_graph()
