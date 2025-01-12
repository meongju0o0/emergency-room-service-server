import requests
from flask import Flask, request, jsonify
from langchain_core.messages import ChatMessage
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__)

class ChatLLM:
    def __init__(self):
        self._model = ChatOllama(model="gemma2:2b", temperature=3)
        self._template = "{question}"
        self._prompt = ChatPromptTemplate.from_template(self._template)

        self._chain = (
            {'question': RunnablePassthrough()}
            | self._prompt
            | self._model
            | StrOutputParser()
        )
    
    def invoke(self, user_input):
        response = self._chain.invoke({'question': user_input})
        return response

llm = ChatLLM()

@app.route("/process-query", methods=["POST"])
def process_query():
    """Dart_Frog 서버와 Postman에서 질의를 처리"""
    try:
        data = request.get_json()
        user_query = data.get("query")
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        response = llm.invoke(user_query)

        dart_frog_url = "http://localhost:8080/medical/nl_query"
        response_data = {"query": user_query, "result": response}

        try:
            dart_frog_response = requests.post(dart_frog_url, json=response_data)
            dart_frog_status = dart_frog_response.status_code
        except requests.exceptions.RequestException as e:
            dart_frog_status = f"Failed to connect to Dart_Frog: {str(e)}"

        return jsonify({
            "status": "success",
            "query": user_query,
            "result": response,
            "dart_frog_status": dart_frog_status
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
