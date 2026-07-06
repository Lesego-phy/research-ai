# Writes the report

from src.agents.llm import azure_llm

def write_node(state: dict) -> dict:
    """
    The Writer Node: Drafts the report based on research and reviewer feedback.
    """
    user_topic = state["user_topic"]
    scraped_docs = state.get("scraped_documents", [])
    reviewer_feedback = state.get("reviewer_feedback")
    revision_count = state.get("revision_count", 0)
    
    #Extract the RAG context from the state
    rag_context = state.get("rag_context", "")

    # In write_node, after the rag_context injection, add:

    academic_context = state.get("academic_context", "")
    if academic_context and "No academic papers" not in academic_context:
        prompt += f"""

    Here are peer-reviewed academic papers on the topic:
    {academic_context}

    IMPORTANT: Cite these academic sources using their titles and authors when referencing their findings.
    """
    
    print(f"[Writer] Drafting report (Revision {revision_count})...")

    #Renamed 'context' to 'web_context' for clarity
    # Format the scraped documents into a readable string for the LLM
    web_context = "\n\n---\n\n".join([f"Source: {doc['url']}\nTitle: {doc['title']}\nContent: {doc['content'][:2000]}..." for doc in scraped_docs])

    #Build the base prompt with the web context
    prompt = f"""You are an expert research report writer. 
    Topic: {user_topic}
    
    Here is the raw web research data you must use:
    {web_context}
    """
    
    # Inject the RAG context into the prompt
    # We only add this if the RAG tool actually found something useful.
    if rag_context and "No documents" not in rag_context and "No relevant" not in rag_context:
        prompt += f"""
    
    Here is additional context from the user's uploaded documents (PDFs):
    {rag_context}
    """

    # Add the reviewer feedback or final instructions
    if reviewer_feedback and revision_count > 0:
        prompt += f"""
    
    CRITICAL: A strict reviewer reviewed your previous draft and provided this feedback:
    "{reviewer_feedback}"
    
    You MUST revise your draft to address all of the reviewer's points. Do not hallucinate facts; only use the provided research data.
    """
    else:
        prompt += """
    
    Write a comprehensive, well-structured, and professional report. Include an Executive Summary, Key Findings, and a Conclusion.
    """

    response = azure_llm.invoke(prompt)
    
    # Increment revision count for the next loop
    return {
        "draft_report": response.content,
        "revision_count": revision_count + 1
    }