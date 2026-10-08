⚙️ Prerequisites
Make sure you have the following installed:
- Python 3.10+
- Ollama
- Git
Download Ollama from:
https://ollama.com

🧠 Install Ollama Model

After installing Ollama, pull a model:

ollama pull llama3.2:3b

ollama list

ollama serve

📦 Install Python Dependencies

Clone the repository:

git clone https://github.com/jaggpython/mcp_project

cd mcp-project

python -m venv venv

Windows

venv\Scripts\activate

macOS / Linux

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run the Application

python -m server.mcp_server

python client/client.py

python -m uvicorn server.app:app --reload --port 8000

streamlit run streamlit_app.py







