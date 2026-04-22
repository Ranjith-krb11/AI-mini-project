from database.vector_db import get_or_create_collection

def retrieve_context(query_text, n_results=3):
    """Searches the vector database for text chunks matching the user's query."""
    collection = get_or_create_collection()
    
    # Check if the database is empty
    if collection.count() == 0:
        return ""
        
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Extract the documents from the ChromaDB response format
    if results and results['documents']:
        return "\n\n---\n\n".join(results['documents'][0])
    
    return ""