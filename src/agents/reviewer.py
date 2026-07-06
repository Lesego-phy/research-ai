#Checks quality and formatting

from src.agents.llm import azure_llm

def reviewer_node(state: dict) -> dict:
    """
    The Review Node: Reviews the draft against the raw data to catch hallucinations.
    """
    draft = state.get("draft_report", "")
    scraped_docs = state.get("scraped_documents", [])
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("MAX_REVISIONS", 3)
    
    print(f"🧐 [Critic] Reviewing draft... (Attempt {revision_count}/{max_revisions})")

    context = "\n\n---\n\n".join([f"Source: {doc['url']}\nContent: {doc['content'][:1500]}..." for doc in scraped_docs])

    prompt = f"""You are a strict, expert fact-checker and critic. 
    Your job is to review a draft report and ensure it contains ZERO hallucinations and is fully supported by the raw research data.
    
    Raw Research Data:
    {context}
    
    Draft Report to Review:
    {draft}
    
    Instructions:
    1. Check every major claim in the draft against the Raw Research Data.
    2. If the draft is accurate, complete, and well-written, respond EXACTLY with: "APPROVED"
    3. If there are hallucinations, missing context, or logical flaws, provide specific, actionable feedback on what the writer needs to fix. Do NOT say "APPROVED".
    """

    response = azure_llm.invoke(prompt)
    feedback = response.content.strip()
    
    is_approved = "APPROVED" in feedback.upper()
    
    # Force approval if we hit the max revision limit to prevent infinite loops
    if revision_count >= max_revisions:
        print("⚠️ [Review] Max revisions reached. Forcing approval.")
        is_approved = True

    return {
        "reviewer_feedback": feedback,
        "is_approved_by_reviewer": is_approved
    }