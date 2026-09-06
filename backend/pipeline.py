"""
Sequential orchestration for the multi-agent research pipeline.

Executes four stages:
  1. Search Agent: Initial discovery of articles and reference links.
  2. Reader Agent: Deep document scraping of the most relevant source.
  3. Writer Chain: Synthesis into a structured research report.
  4. Critic Chain: Objective review, scoring, and actionable feedback.
"""

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> dict:
    """
    Runs the multi-agent pipeline sequentially for the given research topic.

    Args:
        topic (str): The research subject or question.

    Returns:
        dict: Final research state with search results, scraped content, report, and feedback.
    """
    state = {}

    # Stage 1: Search Agent queries web for initial context
    print(f"\n[Stage 1/4] Search Agent gathering sources for: '{topic}'...")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content

    # Stage 2: Reader Agent scrapes deep text from top result
    print("\n[Stage 2/4] Reader Agent scraping top reference source...")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content

    # Stage 3: Writer Chain synthesizes findings into a Markdown report
    print("\n[Stage 3/4] Writer synthesizing final research report...")
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    # Stage 4: Critic Chain evaluates the synthesized report
    print("\n[Stage 4/4] Critic conducting peer review and scoring...")
    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    return state


if __name__ == "__main__":
    user_topic = input("\nEnter a research topic: ").strip()
    if user_topic:
        run_research_pipeline(user_topic)
    else:
        print("No topic provided. Exiting.")
