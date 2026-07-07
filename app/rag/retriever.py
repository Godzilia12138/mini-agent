from app.rag.indexer import search, get_stats, list_sources


def format_search_results(results: list[dict]) -> str:
    if not results:
        return "知识库中未找到与查询相关的内容。"

    lines = [f"找到 {len(results)} 条相关片段：\n"]
    for i, r in enumerate(results, 1):
        score_pct = int(r["score"] * 100)
        lines.append(f"### [{i}] {r['source']}（相关度 {score_pct}%）")
        lines.append(r["text"])
        lines.append("")
    return "\n".join(lines)


def rag_search(query: str, top_k: int = 5) -> str:
    results = search(query, top_k=top_k)
    return format_search_results(results)
