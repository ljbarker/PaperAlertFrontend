import os
import reflex as rx
import requests

API_URL = "http://127.0.0.1:5000/query"  # Change this if backend runs on a different IP

class QA(rx.Base):
    """A question and answer pair."""
    question: str
    answer: str

DEFAULT_CHATS = {
    "Intros": [],
}

class State(rx.State):
    """The app state."""
    chats: dict[str, list[QA]] = DEFAULT_CHATS
    current_chat = "Intros"
    question: str
    processing: bool = False
    new_chat_name: str = ""

    def create_chat(self):
        """Create a new chat."""
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]

    def set_chat(self, chat_name: str):
        """Set the name of the current chat."""
        self.current_chat = chat_name

    @rx.var(cache=True)
    def chat_titles(self) -> list[str]:
        """Return list of chat names."""
        return list(self.chats.keys())

    async def process_question(self, form_data: dict[str, str]):
        """Send user query to backend and update chat with the response."""
        question = form_data["question"]
        if not question:
            return

        self.chats[self.current_chat].append(QA(question=question, answer=""))
        self.processing = True
        yield

        # Send the query to the backend
        try:
            response = requests.post(API_URL, json={"query": question})
            response_data = response.json()
            answer = response_data.get("response", "No response from backend.")
        except Exception as e:
            answer = f"Error communicating with backend: {e}"

        self.chats[self.current_chat][-1].answer = answer
        self.chats = self.chats
        self.processing = False
        yield
