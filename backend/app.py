from flask import Flask, request, jsonify
from flask_cors import CORS
from shared.search.arxiv_search import search_papers, summarize_papers
from shared.notifications.email import send_email
from agent_handler import handle_openai_response

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

@app.route("/query", methods=["POST"])
def query_papers():
    """
    API endpoint to process a user query, search papers, and return the results.
    """
    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "Query parameter is missing"}), 400

    try:
        # Process query through OpenAI Agent
        response = handle_openai_response(user_query)

        print("DEBUG: Response from handle_openai_response:", response)  # Debugging

        # Ensure response is valid JSON
        if isinstance(response, dict):
            if "email_scheduled" in response:
                message = (
                    f"📬 Email notifications for **{response['topic']}** have been scheduled.\n"
                    f"✅ First email: {response['first_email']}\n"
                    f"✅ Next email: {response['next_email']}"
                )
            elif "summaries" in response:
                message = "\n".join(response["summaries"])  # Properly format summaries
            else:
                message = "No relevant papers found."
        else:
            message = str(response)  # Convert any unexpected response to a string

        return jsonify({"response": message})  # Ensure JSON response

    except Exception as e:
        print("ERROR in query_papers:", e)
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
