from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ConsultingState


def _get_model(api_key: str) -> ChatAnthropic:
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=1024,
    )


# ─────────────────────────────────────────
# Node 1: 課題分析 Agent
# ─────────────────────────────────────────
def issue_analysis_node(state: ConsultingState) -> ConsultingState:
    """
    クライアント情報を受け取り、根本課題・定量インパクト・AI適用優先度を分析する。
    """
    model = _get_model(state["_api_key"])

    messages = [
        SystemMessage(content="""あなたは経験豊富なビジネスコンサルタントです。
クライアントの課題を深く分析し、以下の観点で整理してください：
1. 根本課題（表面的な課題の背景にある本質）
2. 定量的インパクト（現状の損失・コスト試算）
3. AI適用の優先度（高/中/低）とその理由
回答は日本語で、簡潔かつ洞察に富む内容にしてください。200〜250字。"""),
        HumanMessage(content=f"以下のクライアント情報を分析してください：\n\n{state['client_input']}")
    ]

    response = model.invoke(messages)
    return {
        **state,
        "issue_analysis": response.content,
        "current_agent": "roi_estimation",
    }


# ─────────────────────────────────────────
# Node 2: ROI試算 Agent
# ─────────────────────────────────────────
def roi_estimation_node(state: ConsultingState) -> ConsultingState:
    """
    課題分析の結果を受け取り、投資対効果を具体的な数字で試算する。
    """
    model = _get_model(state["_api_key"])

    context = f"""【クライアント情報】
{state['client_input']}

【課題分析結果】
{state['issue_analysis']}"""

    messages = [
        SystemMessage(content="""あなたは財務モデリングの専門家です。
前段の課題分析を踏まえ、AI導入のROIを試算してください：
- 初期投資額の目安（概算）
- 年間削減コスト・創出価値
- 投資回収期間
- 3年間の期待累計効果
具体的な数字を使い、根拠も簡潔に示してください。200〜250字。"""),
        HumanMessage(content=context)
    ]

    response = model.invoke(messages)
    return {
        **state,
        "roi_estimation": response.content,
        "current_agent": "roadmap",
    }


# ─────────────────────────────────────────
# Node 3: ロードマップ Agent
# ─────────────────────────────────────────
def roadmap_node(state: ConsultingState) -> ConsultingState:
    """
    課題分析・ROI試算を踏まえ、3フェーズの実行ロードマップを設計する。
    """
    model = _get_model(state["_api_key"])

    context = f"""【クライアント情報】
{state['client_input']}

【課題分析】
{state['issue_analysis']}

【ROI試算】
{state['roi_estimation']}"""

    messages = [
        SystemMessage(content="""あなたはプロジェクトマネジメントの専門家です。
AI導入の実行ロードマップを3フェーズで設計してください：
Phase 1（〜3ヶ月）：PoC・基盤整備
Phase 2（3〜6ヶ月）：パイロット展開
Phase 3（6ヶ月〜）：本番展開・最適化
各フェーズの主要タスクと成功指標（KPI）を明示してください。200〜250字。"""),
        HumanMessage(content=context)
    ]

    response = model.invoke(messages)
    return {
        **state,
        "roadmap": response.content,
        "current_agent": "final_proposal",
    }


# ─────────────────────────────────────────
# Node 4: 提案書サマリー Agent
# ─────────────────────────────────────────
def final_proposal_node(state: ConsultingState) -> ConsultingState:
    """
    全エージェントの出力を統合し、経営者向け提案書サマリーを生成する。
    """
    model = _get_model(state["_api_key"])

    context = f"""【クライアント情報】
{state['client_input']}

【課題分析】
{state['issue_analysis']}

【ROI試算】
{state['roi_estimation']}

【実行ロードマップ】
{state['roadmap']}"""

    messages = [
        SystemMessage(content="""あなたはエグゼクティブ向けプレゼン資料作成の専門家です。
全エージェントの分析を統合し、経営者向けの提案サマリーを作成してください。

■ エグゼクティブサマリー（3行）
■ 推奨AI技術・アーキテクチャ
■ 期待されるビジネス成果（数値付き）
■ 次のアクション（具体的な3ステップ）

説得力があり、意思決定を促す内容にしてください。250〜300字。"""),
        HumanMessage(content=context)
    ]

    response = model.invoke(messages)
    return {
        **state,
        "final_proposal": response.content,
        "current_agent": "done",
    }
