import spacy
import networkx as nx

# Try to load model, download if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def build_mindmap(text):
    doc = nlp(text)
    G = nx.DiGraph()
    main_node = text.strip().capitalize()
    G.add_node(main_node)

    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ("nsubj", "dobj", "pobj") and token.head.pos_ in ("VERB", "NOUN"):
                G.add_node(token.head.text.capitalize())
                G.add_node(token.text.capitalize())
                G.add_edge(token.head.text.capitalize(), token.text.capitalize())
                G.add_edge(main_node, token.head.text.capitalize())

    return G
