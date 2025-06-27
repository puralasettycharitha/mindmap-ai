import spacy
import subprocess
import sys
import networkx as nx

# Load model or download if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def build_mindmap(text):
    doc = nlp(text)
    G = nx.DiGraph()

    root = text.strip().capitalize()
    G.add_node(root)

    for chunk in doc.noun_chunks:
        concept = chunk.text.strip().capitalize()
        if concept.lower() != root.lower():
            G.add_node(concept)
            G.add_edge(root, concept)

    return G
