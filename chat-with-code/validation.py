fallback_response = (
    "I'm sorry, I couldn't find an answer for that — can I help with something else?"
)


def codex_validated_query(query_engine, project, user_query):
    # Step 1: Get response from your RAG pipeline
    response_obj = query_engine.query(user_query)
    initial_response = str(response_obj)

    # Step 2: Convert to message format
    context = response_obj.source_nodes
    context_str = "\n".join([n.node.text for n in context])

    # prompt_template = (
    #     "Context information is below.\n"
    #     "---------------------\n"
    #     "{context}\n"
    #     "---------------------\n"
    #     "Given the context information above I want you to think step by step to answer the query in a crisp manner, incase case you don't know the answer say 'I don't know!'.\n"
    #     "Query: {query}\n"
    #     "Answer: "
    # )

    prompt_template = (
        "Context information is below.\n"
        "---------------------\n"
        "{context}\n"
        "---------------------\n"
        "Given the context information above, I want you to think step by step to answer the query in a crisp manner. "
        "First, carefully check if the answer can be found in the provided context. "
        "If the answer is available in the context, use that information to respond. "
        "If the answer is not available in the context or the context is insufficient, "
        "you may use your own knowledge to provide a helpful response. "
        "Only say 'I don't know!' if you cannot answer the question using either the context or your general knowledge.\n"
        "Query: {query}\n"
        "Answer: "
    )

    user_prompt = prompt_template.format(context=context_str, query=user_query)
    messages = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    # Step 3: Validate with Codex
    result = project.validate(
        messages=messages,
        query=user_query,
        context=context_str,
        response=initial_response,
    )

    # Step 4: Return Codex-evaluated final response
    final_response = (
        result.expert_answer
        if result.expert_answer and result.escalated_to_sme
        else fallback_response if result.should_guardrail else initial_response
    )

    # Step 5: Return both final response and full validation info
    trust_score = result.model_dump()["eval_scores"]["trustworthiness"]["score"]
    
    # Determine emoji based on score
    if trust_score >= 0.8:
        emoji = "🟢"
    elif trust_score >= 0.5:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    return emoji, trust_score, final_response
