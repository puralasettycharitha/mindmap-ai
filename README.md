# 🧠 MindMap AI — Auto Sketch Your Thinking

MindMap AI is a smart app that takes your ideas or problem statements and **automatically generates interactive visual mind maps**. It uses **natural language processing (NLP)** to extract concepts and relationships, and plots them using Dash + Cytoscape.

🚀 [Live Demo on Render](https://mindmap-ai-i4ce.onrender.com) ← *replace with your actual URL*

---

## ✨ Features

- 📝 Input free-form text like: _"Build a food delivery app with real-time tracking"_
- 🧠 NLP-powered concept extraction (nouns, verbs, adjectives, root verbs)
- 🎨 Color-coded node types (noun/verb/adj/root)
- 🔄 Layout switching (tree, circle, grid, etc.)
- 💾 Export/Import mind maps as JSON
- 🖼 Export as PNG
- 📦 Built with Python, Dash, spaCy, and NetworkX

---

## 🛠 Tech Stack

- [Dash](https://dash.plotly.com/)
- [Dash Cytoscape](https://dash.plotly.com/cytoscape)
- [spaCy](https://spacy.io/)
- [NetworkX](https://networkx.org/)
- Hosted on [Render.com](https://render.com)

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/your-username/mindmap-ai.git
cd mindmap-ai
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
