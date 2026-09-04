"""
CLI execution pipeline for the Multi-Agent Research System.

Executes the four-stage research workflow sequentially:
  Stage 1: Search Agent queries the web for initial sources and insights.
  Stage 2: Reader Agent scrapes the most relevant source for deeper context.
  Stage 3: Writer Chain synthesizes findings into a comprehensive report.
  Stage 4: Critic Chain evaluates quality and offers actionable feedback.
"""

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> dict:
    """
    Executes the full multi-agent research workflow for a given topic.

    Args:
        topic (str): The research subject or question.

    Returns:
        dict: Collected results containing search results, scraped content,
              the final report, and critic feedback.
    """
    state = {}

    # -------------------------------------------------------------------------
    # Stage 1: Search Agent (Broad topic discovery)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print(f"Step 1 - Search Agent exploring topic: '{topic}'...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    print("\n[Search Results Summary]:\n", state["search_results"])

    # -------------------------------------------------------------------------
    # Stage 2: Reader Agent (Deep document scraping)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("Step 2 - Reader Agent scraping top reference source...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    print("\n[Scraped Content Preview]:\n", state["scraped_content"][:500], "...\n")

    # -------------------------------------------------------------------------
    # Stage 3: Writer Chain (Report generation)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("Step 3 - Writer synthesizing findings into final report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    print("\n[Generated Report]:\n", state["report"])

    # -------------------------------------------------------------------------
    # Stage 4: Critic Chain (Peer review and quality check)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("Step 4 - Critic performing peer review & scoring...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })
    print("\n[Critic Review]:\n", state["feedback"])

    return state


if __name__ == "__main__":
    user_topic = input("\nEnter a research topic: ").strip()
    if user_topic:
        run_research_pipeline(user_topic)
    else:
        print("No topic provided. Exiting.")
