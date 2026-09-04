"""
Multi-Agent Definitions for the Collaborative Research Platform.

This module sets up:
1. Search Agent: Uses Tavily web search tool to find relevant recent articles.
2. Reader Agent: Uses web scraping to extract deep page contents from top URLs.
3. Writer Chain: Synthesizes gathered research into a structured research report.
4. Critic Chain: Evaluates the report for accuracy, depth, and clarity.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent as create_agent
from tools import web_search, scrape_url

# Load API keys and environment variables from .env
load_dotenv()

# Shared LLM instance for agents and prompt chains
# Using temperature=0 to ensure consistent, factual research summaries
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ---------------------------------------------------------------------------
# 1. Search Agent
# ---------------------------------------------------------------------------
def build_search_agent():
    """
    Builds a ReAct agent equipped with the Tavily web search tool.
    Responsible for initial topic discovery and finding relevant sources.
    """
    return create_agent(
        model=llm,
        tools=[web_search]
    )


# ---------------------------------------------------------------------------
# 2. Reader Agent
# ---------------------------------------------------------------------------
def build_reader_agent():
    """
    Builds a ReAct agent equipped with the URL scraper tool.
    Responsible for reading the most promising webpage from search results
    and pulling in-depth text content.
    """
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


# ---------------------------------------------------------------------------
# 3. Writer Chain
# ---------------------------------------------------------------------------
# Prompts the model to synthesize both surface search snippets and deeper scraped content
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ---------------------------------------------------------------------------
# 4. Critic Chain
# ---------------------------------------------------------------------------
# Provides objective scoring and actionable feedback on the generated draft
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
