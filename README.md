---
title: CONSUL-AI
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# CONSUL-AI — Multi-Agent Consulting Orchestration

> **LangGraph + FastAPI + Claude Sonnet による、コンサルティング業務AIエージェント化デモ**

## アーキテクチャ

```
クライアント入力
      │
      ▼
┌─────────────────────────────────────────┐
│           LangGraph Workflow             │
│                                         │
│  [課題分析] → [ROI試算] → [ロードマップ] → [提案書] │
│                                         │
│  各ノードが ConsultingState を更新・引き継ぐ  │
└─────────────────────────────────────────┘
      │ SSE (Server-Sent Events)
      ▼
  FastAPI /api/run
      │
      ▼
  フロントエンド (リアルタイム表示)
```

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| エージェント基盤 | LangGraph 0.2 |
| LLM | Claude Sonnet (Anthropic) |
| バックエンド | FastAPI + uvicorn |
| ストリーミング | Server-Sent Events (SSE) |
| フロントエンド | Vanilla HTML/CSS/JS |
| デプロイ | HuggingFace Spaces (Docker) |

## エージェント構成

### 1. 課題分析 Agent (`issue_analysis_node`)
クライアント情報を受け取り、根本課題・定量インパクト・AI適用優先度を分析。

### 2. ROI試算 Agent (`roi_estimation_node`)
前段の課題分析を踏まえ、初期投資・年間削減コスト・回収期間を試算。

### 3. ロードマップ Agent (`roadmap_node`)
Phase 1〜3 の実行計画とKPIを設計。

### 4. 提案書サマリー Agent (`final_proposal_node`)
全エージェントの出力を統合し、経営者向けエグゼクティブサマリーを生成。

## ローカル起動

```bash
# 依存関係インストール
pip install -r requirements.txt

# 起動
uvicorn app:app --reload --port 8000
```

ブラウザで `http://localhost:8000` を開き、Anthropic APIキーを入力してください。

## ファイル構成

```
consul-ai/
├── app.py              # FastAPI エントリーポイント + SSEエンドポイント
├── graph/
│   ├── state.py        # ConsultingState (TypedDict)
│   ├── nodes.py        # 4つのエージェントノード
│   └── workflow.py     # LangGraphグラフ定義
├── frontend/
│   └── index.html      # SPA フロントエンド
├── requirements.txt
├── Dockerfile          # HF Spaces用
└── README.md
```

## LangGraph のポイント

```python
# workflow.py — グラフ定義の核心部分
workflow = StateGraph(ConsultingState)

workflow.add_node("issue_analysis", issue_analysis_node)
workflow.add_node("roi_estimation", roi_estimation_node)
workflow.add_node("roadmap", roadmap_node)
workflow.add_node("final_proposal", final_proposal_node)

workflow.set_entry_point("issue_analysis")
workflow.add_edge("issue_analysis", "roi_estimation")
workflow.add_edge("roi_estimation", "roadmap")
workflow.add_edge("roadmap", "final_proposal")
workflow.add_edge("final_proposal", END)
```

各ノードは `ConsultingState` を受け取り、自分のフィールドだけ更新して返す。
これによりエージェント間のコンテキスト共有が型安全に実現される。
