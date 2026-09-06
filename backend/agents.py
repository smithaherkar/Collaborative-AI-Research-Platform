"""
Multi-Agent definitions and LangChain prompt chains for research synthesis.

Architecture:
1. Search Agent: Uses Tavily API to locate top articles and current data.
2. Reader Agent: Scrapes the most promising URL for in-depth source text.
3. Writer Chain: Synthesizes search snippets and scraped text into a Markdown report.
4. Critic Chain: Reviews the report, provides structured feedback, and scores it out of 10.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent as create_agent
from tools import web_search, scrape_url

# Load environment configuration
env_root = Path(__file__).resolve().parent.parent / ".env"
if env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY") or "sk-placeholder-key-for-initialization"

# Shared OpenAI chat model instance (temperature=0 ensures factual consistency)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)


# ---------------------------------------------------------------------------
# 1. Search Agent
# ---------------------------------------------------------------------------
def build_search_agent():
    """
    Creates a ReAct agent powered by Tavily web search
    to gather high-relevance source links and initial findings.
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
    Creates a ReAct agent equipped with BeautifulSoup scraping
    to extract in-depth content from the best candidate URL.
    """
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


# ---------------------------------------------------------------------------
# 3. Writer Chain
# ---------------------------------------------------------------------------
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
