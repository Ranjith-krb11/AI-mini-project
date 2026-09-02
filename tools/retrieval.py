from typing import Optional, List, Dict, Any, Tuple
from database.vector_db import get_or_create_collection


def retrieve_context_with_citations(
    query_text: str,
    user_id: Optional[int] = None,
    n_results: int = 4
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Searches the vector database for relevant chunks isolated to the specified user_id.
    Returns:
        (formatted_context_string, list_of_citation_dicts)
    """
    collection = get_or_create_collection()

    if collection.count() == 0:
        return "", []

    # Apply strict metadata filter by user_id if provided
    where_filter = {"user_id": user_id} if user_id is not None else None

    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )
    except Exception:
        # Fallback if where query fails or collection empty
        results = None

    if not results or not results.get("documents") or not results["documents"][0]:
        return "", []

    docs = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

    context_parts = []
    citations = []
    seen_citations = set()

    for idx, doc_text in enumerate(docs):
        meta = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
        source = meta.get("source", "Unknown document")
        page = meta.get("page_number", 1)
        doc_id = meta.get("document_id", "")
        chunk_no = meta.get("chunk_number", idx)

        citation_key = f"{source}:{page}"
        if citation_key not in seen_citations:
            seen_citations.add(citation_key)
            citations.append({
                "source": source,
                "page_number": page,
                "chunk_number": chunk_no,
                "document_id": doc_id
            })

        context_parts.append(f"[{source} - Page {page}]:\n{doc_text}")

    context_str = "\n\n---\n\n".join(context_parts)
    return context_str, citations


def retrieve_context(
    query_text: str,
    n_results: int = 3,
    user_id: Optional[int] = None
) -> str:
    """
    Backwards-compatible retrieval function returning joined context string.
    Supports user_id isolation filter.
    """
    context, _ = retrieve_context_with_citations(query_text, user_id=user_id, n_results=n_results)
    return context