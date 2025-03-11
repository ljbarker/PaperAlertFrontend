import openai
import re
import json  # Import the json module for parsing
from shared.search.arxiv_search import search_papers, summarize_papers
from shared.notifications.email import send_email
import schedule
import time
from openai import OpenAI
import threading

# Set up OpenAI API key
client = OpenAI(
    api_key="",
)

def interpret_user_query(query):
    """
    Use OpenAI to interpret the user query and return a structured response.
    Args:
        query (str): The user's input query.
    Returns:
        dict: Contains the topic, task type (search or schedule), and frequency (if applicable).
    """
    prompt = f"""
    Analyze the following user query and extract the topic of interest, whether the user wants periodic email updates, the frequency (weekly, daily, monthly, or none), and the number requested. Respond in this JSON format:
    {{
        "topic": "string",
        "send_email": true or false,
        "frequency": "none", "weekly", "daily", or "monthly",
        "number": "number"
    }}
    Query: "{query}"
    """

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )


    response_text = ""
    for chunk in response:
        response_text += chunk.choices[0].delta.content or ""

    response_text = clean_response(response_text)
       
    try:
        result_json = json.loads(response_text)  # Parse JSON from OpenAI response
        return result_json
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response received:", response_text)
        raise

def clean_response(response_text):
    """
    Remove '''json and ''' tags from the response if they exist.
    """
    # Remove starting '''json and ending '''
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove '''json
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove '''

    # Strip any leading or trailing whitespace
    return response_text.strip()


def reorder_papers_by_relevance(topic, papers, quantity):
    """
    Reorder papers based on relevance to the specified topic using OpenAI.
    """
    paper_summaries = json.dumps(papers)
    prompt = f"""
    You are given a list of research papers related to the topic '{topic}'. Here are the papers: '{paper_summaries}'.
    Reorder these papers from most relevant to least relevant based on their titles and summaries, cutting the number of papers to the '{quantity}' most relevant.
    Return the reordered list as JSON with the same structure as the input and no additional content, explanation, or rationale.
    """

    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )

    response_text = ""
    for chunk in response:
        response_text += chunk.choices[0].delta.content or ""

    response_text = clean_response(response_text)
       
    try:
        result_json = json.loads(response_text)  # Parse JSON from OpenAI response
        return result_json
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response received:", response_text)
        raise


def handle_openai_response(query):
    """
    Handle the task based on OpenAI's interpretation of the query.
    Args:
        query (str): The user's query.
    
    Returns:
        dict: A structured response containing either summaries or an email confirmation.
    """
    response = interpret_user_query(query)

    print("Here is the response for debugging:", response)

    topic = response.get("topic", "")
    send_email_updates = response.get("send_email", False)
    frequency = response.get("frequency", "none")
    quantity = response.get("number", 5)

    # Perform the arXiv search
    papers = search_papers(topic, quantity)
    ordered_papers = reorder_papers_by_relevance(topic, papers, quantity)

    if send_email_updates:
        # Prepare email content
        subject = f"Updates on {topic}"
        body = summarize_papers(ordered_papers)

        if frequency != "none":
            # Schedule periodic notifications
            schedule_periodic_updates(topic, "lornstil@gmail.com", subject, body, frequency)
            print("about to return here")
            return {
                "email_scheduled": True,
                "topic": topic,
                "first_email": "Scheduled in 7 days" if frequency == "weekly" else "Scheduled in 24 hours",
                "next_email": f"Every {frequency}"
            }
        else:
            # One-time email notification
            result = send_email("lornstil@gmail.com", subject, body)
            return {"email_sent": result, "topic": topic}
    
    else:
        # Return paper summaries for immediate display
        return {"summaries": summarize_papers(ordered_papers)}

def run_scheduler():
    """Run the scheduler in a background thread."""
    while True:
        schedule.run_pending()
        time.sleep(1)

def schedule_periodic_updates(topic, recipient_email, subject, body, frequency):
    """
    Schedule periodic email updates based on the specified frequency.
    Args:
        topic (str): The search topic.
        recipient_email (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email content.
        frequency (str): The frequency of updates ('weekly', 'daily', etc.).
    """
    if frequency == "weekly":
        schedule.every().week.do(send_email, recipient_email, subject, body)
    elif frequency == "daily":
        schedule.every().day.do(send_email, recipient_email, subject, body)
    elif frequency == "monthly":
        schedule.every(30).days.do(send_email, recipient_email, subject, body)

    print(f"✅ Scheduled {frequency} updates on '{topic}' for {recipient_email}")

    # Start scheduler in a separate thread (only once)
    if not hasattr(schedule_periodic_updates, "scheduler_started"):
        schedule_periodic_updates.scheduler_started = True  # Prevent multiple threads
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
