import arxiv

def search_papers(topic, max_results):
    """
    Search arXiv for the newest papers based on the given topic.

    Args:
        topic (str): The search query, e.g., 'machine learning' or 'quantum computing'.
        max_results (int): The number of recent papers to retrieve.

    Returns:
        list: A list of dictionaries containing information about the papers.
    """
    search = arxiv.Search(
        query=topic,
        max_results=int(max_results)+10,
        sort_by=arxiv.SortCriterion.SubmittedDate,  # Sort by newest submissions
    )

    papers = []
    for result in search.results():
        papers.append({
            "id": result.entry_id,
            "title": result.title,
            "link": result.pdf_url,
            "summary": result.summary
        })

    return papers


def summarize_papers(papers):
    """
    Summarize the list of papers with their titles, summaries, and links.

    Args:
        papers (list): The list of papers returned from arxiv.

    Returns:
        str: A formatted string with summaries of the papers.
    """
    if not papers:
        return "No papers found for the given topic."

    summary = "Here are the recent papers: "
    for paper in papers:
        summary += f"- **{paper['title']}**"
        summary += f"  {paper['summary'][:300]}..."
        summary += f"  [Read More]({paper['link']})"

    return summary
