from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_scraper, web_search
import os

from config import get_settings

from dotenv import load_dotenv

load_dotenv()   



llm = ChatGroq(
    api_key = get_settings().GROQ_API_KEY,
    model = "llama-3.3-70b-versatile",
    verbose=True
)



def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]

    )


def build_research_agent():
    return create_agent(
        model = llm,
        tools = [web_scraper]

    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Professional Writer Agent in a Multi-Agent Research System. "
     "You receive raw research findings, scraped content, and search summaries from other agents. "
     "Your job is to transform this raw data into a polished, well-structured, and engaging article. "
     "Follow these guidelines:\n"
     "- Write in a clear, authoritative, and professional tone.\n"
     "- Organize the content with a compelling introduction, logically ordered sections, and a concise conclusion.\n"
     "- Cite all sources with their URLs inline.\n"
     "- Eliminate redundancy and ensure every paragraph adds unique value.\n"
     "- Highlight key insights, statistics, and takeaways.\n"
     "- Use markdown formatting (headings, bullet points, bold) for readability.\n"
     "- Ensure factual accuracy — do not hallucinate or add information not present in the research."
    ),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])


chain = writer_prompt | llm | StrOutputParser()

critics_prompt = ChatPromptTemplate.from_messages([
    ("system",
    """
You are a Peer Review Agent in a Multi-Agent Research System. 
    Your role is to act as a critical reviewer for the content produced by the Writer Agent.
    You must evaluate the article based on clarity, accuracy, organization, completeness, 
    and adherence to the original research. Identify strengths, weaknesses, and areas 
    that need improvement.
    Provide actionable feedback to help the writer enhance the quality of the article.
    
    Guidelines:
    - Be thorough but fair in your assessment.
    - Point out specific areas that lack clarity or detail.
    - Verify that all claims are supported by the provided research.
    - Suggest improvements in structure, flow, and conciseness.
    - Identify any factual inaccuracies or unsubstantiated claims.
    - Suggest additional information that should be included.
    - Provide an overall quality score (0-10) along with your detailed feedback.
    """
    ),
    ("user", "Here is the article to review:\n\n{article}\n\nProvide your detailed critique.")
])


critics_chain = critics_prompt | llm | StrOutputParser()


