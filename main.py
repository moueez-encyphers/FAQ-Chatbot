from openai import OpenAI
from flask import Flask, render_template, request, url_for, session, redirect
import os

API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)

faq_data = """
1. Hours: We are open Monday to Friday, from 9 AM to 6 PM.
2. Location: Our office is located at 123 Main Street, Springfield.
3. Contact: You can reach us at support@example.com or call +1-555-1234.
4. Services: We offer web development, app development, and digital marketing services.
5. Pricing: Our pricing depends on the project. Please contact sales@example.com for a quote.
"""


def chatbot_response(user_input):
    prompt = f"""
    You are a helpful FAQ chatbot. Answer the user only using the information below:

    {faq_data}

    If the question is unrelated, politely say you don’t know.

    User: {user_input}
    Chatbot:
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper + fast model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content

# print(chatbot_response("When do you open?"))


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def home():
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "clear":
            session["chat_history"] = []
            session.modified = True
            return redirect(url_for("home"))

        user_message = request.form.get("message")
        if user_message:
            # Save user message
            session["chat_history"].append({"role": "user", "content": user_message})

            # Get response from OpenAI
            try:
                reply = chatbot_response(session["chat_history"])

                # Save chatbot reply
                session["chat_history"].append({"role": "assistant", "content": reply})

            except Exception as e:
                session["chat_history"].append({"role": "assistant", "content": f"Error: {str(e)}"})

            session.modified = True
        return redirect(url_for("home"))

    return render_template("index.html", chat_history=session["chat_history"])


@app.route("/clear")
def clear():
    session["chat_history"] = []
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
