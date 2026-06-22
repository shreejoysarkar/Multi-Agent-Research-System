"""
Multi-Agent Research Pipeline
==============================
Orchestrates a four-stage research workflow:
  1. Search  – discover relevant sources via web search
  2. Research – scrape full content from discovered URLs
  3. Write   – synthesise a polished article from raw research
  4. Critique – peer-review the article and provide feedback

Can be run standalone (CLI) or driven by the Streamlit UI via the
`on_status` callback for live progress updates.
"""

import time
import re
import sys
from typing import Callable, Optional

from agent import build_search_agent, build_research_agent, critics_chain, writer_chain
from tools import web_scraper


MAX_RETRIES = 3


# ── Helpers ──────────────────────────────────────────────────────────────────

def _safe_print(msg: str):
    """Print to console, replacing chars that Windows cp1252 can't encode."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        ))


def invoke_agent_with_retry(
    agent,
    payload: dict,
    stage_name: str,
    on_status: Optional[Callable] = None,
) -> dict:
    """Invoke a LangChain agent with retry logic for Groq tool-call failures."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return agent.invoke(payload)
        except Exception as e:
            error_msg = str(e)
            if "tool_use_failed" in error_msg or "400" in error_msg:
                msg = f"[!] {stage_name}: Groq tool-call error (attempt {attempt}/{MAX_RETRIES}). Retrying..."
                _safe_print(f"\n  {msg}")
                if on_status:
                    on_status(msg)
                time.sleep(2 * attempt)
            else:
                raise
    msg = f"[X] {stage_name}: All {MAX_RETRIES} retries exhausted."
    _safe_print(f"\n  {msg}")
    if on_status:
        on_status(msg)
    return None


def extract_urls(text: str) -> list[str]:
    """Pull http(s) URLs out of a block of text."""
    return re.findall(r'https?://[^\s\)\]\"\']+', text)


def extract_all_urls_from_messages(result: dict) -> list[str]:
    """Extract URLs from *every* message in an agent response.

    The agent's final AI message often summarises results and drops raw URLs.
    Tool-call result messages always contain the raw tool output (which has
    the URLs).  Scanning all messages ensures we never miss them.
    """
    seen: set[str] = set()
    urls: list[str] = []
    for msg in result.get("messages", []):
        text = ""
        if hasattr(msg, "content") and isinstance(msg.content, str):
            text = msg.content
        elif isinstance(msg, tuple) and len(msg) >= 2:
            text = str(msg[1])
        for url in extract_urls(text):
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


# ── Pipeline ─────────────────────────────────────────────────────────────────

def run_pipeline(
    topic: str,
    on_status: Optional[Callable] = None,
) -> dict:
    """
    Execute the full multi-agent research pipeline.

    Parameters
    ----------
    topic : str
        The research topic / query.
    on_status : callable, optional
        ``on_status(message: str)`` is called with human-readable progress
        updates so a UI layer (e.g. Streamlit) can display them live.

    Returns
    -------
    dict with keys: search_result, scraped_content, report, feedback.
    Partial results are returned if a stage fails.
    """

    def _status(msg: str):
        """Send status to both console (ASCII-safe) and UI callback (full Unicode)."""
        _safe_print(msg.encode("ascii", errors="replace").decode("ascii"))
        if on_status:
            on_status(msg)

    state = {}

    # ── Stage 1: Search ──────────────────────────────────────────────
    _status("Stage 1 / 4 -- Search Agent is discovering sources...")

    search_agent = build_search_agent()
    search_result = invoke_agent_with_retry(
        search_agent,
        {"messages": [("user", f"Find recent and reliable information about: {topic}")]},
        "Search Agent",
        on_status=on_status,
    )

    if search_result is None:
        _status("[X] Search Agent failed after retries. Aborting.")
        return state

    # Store the final AI summary
    state["search_result"] = search_result["messages"][-1].content

    # Extract URLs from ALL messages (tool results have the raw URLs;
    # the final AI summary often drops them).
    all_urls = extract_all_urls_from_messages(search_result)
    if not all_urls:
        all_urls = extract_urls(state["search_result"])
    urls = list(dict.fromkeys(all_urls))  # de-dup, preserve order

    _status(f"[OK] Search complete -- {len(urls)} source URL(s) discovered.")
    state["urls"] = urls

    # ── Stage 2: Research (scrape) ───────────────────────────────────
    _status("Stage 2 / 4 -- Research Agent is scraping content...")

    research_agent = build_research_agent()
    url_list = "\n".join(urls[:5]) if urls else "No URLs found"

    result = invoke_agent_with_retry(
        research_agent,
        {"messages": [("user",
            f"Here are URLs about '{topic}'. Use the web_scraper tool to "
            f"scrape the most relevant one and return its full content.\n\n"
            f"URLs:\n{url_list}"
        )]},
        "Research Agent",
        on_status=on_status,
    )

    if result is None and urls:
        _status("[!] Research Agent failed. Falling back to direct scraping...")
        state["scraped_content"] = web_scraper.invoke(urls[0])
    elif result is None:
        _status("[X] Research Agent failed and no URLs to fall back on. Aborting.")
        return state
    else:
        state["scraped_content"] = result["messages"][-1].content

    _status("[OK] Research complete -- content extracted.")

    # ── Stage 3: Write ───────────────────────────────────────────────
    _status("Stage 3 / 4 -- Writer Agent is drafting the article...")

    combined_research = (
        f"Search results:\n{state['search_result']}\n\n"
        f"Detailed Scraped result:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "input": (
            f"Topic: {topic}\n\n"
            f"Raw Research Data:\n{combined_research}\n\n"
            "Using the research data above, write a comprehensive, well-structured, "
            "and engaging article on this topic. Cite sources with URLs."
        )
    })

    _status("[OK] Article drafted successfully.")

    # ── Stage 4: Critique ────────────────────────────────────────────
    _status("Stage 4 / 4 -- Critic Agent is reviewing the article...")

    state["feedback"] = critics_chain.invoke({
        "article": state["report"]
    })

    _status("[OK] Critique complete. Pipeline finished!")

    return state


# ── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        user_topic = " ".join(sys.argv[1:])
    else:
        user_topic = input("Enter your research topic: ").strip()
        if not user_topic:
            print("No topic provided. Exiting.")
            sys.exit(1)

    results = run_pipeline(user_topic)
    if "report" in results:
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(results["report"])
    if "feedback" in results:
        print("\n" + "=" * 60)
        print("CRITIC FEEDBACK")
        print("=" * 60)
        print(results["feedback"])
