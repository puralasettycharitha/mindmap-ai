import spacy
import networkx as nx

nlp = spacy.load("en_core_web_sm")

def build_mindmap(text):
    doc = nlp(text)
    G = nx.Graph()

    for token in doc:
        if token.dep_ not in ("punct", "det"):
            G.add_node(token.text)
            if token.head != token:
                G.add_edge(token.head.text, token.text)

    nodes = [{"data": {"id": n, "label": n}} for n in G.nodes()]
    edges = [{"data": {"source": u, "target": v}} for u, v in G.edges()]
    return nodes + edges
