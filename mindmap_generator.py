# 🔧 mindmap_generator.py

import spacy
import networkx as nx

import spacy
nlp = spacy.load("en_core_web_sm")


def build_mindmap(text):
    doc = nlp(text)
    G = nx.DiGraph()

    for sent in doc.sents:
        for token in sent:
            if not token.is_alpha or token.is_stop:
                continue

            token_type = get_type(token)
            G.add_node(token.text, type=token_type, tooltip=token_type)

            if token.head != token and token.head.is_alpha:
                head_type = get_type(token.head)
                G.add_node(token.head.text, type=head_type, tooltip=head_type)
                G.add_edge(token.head.text, token.text, label=token.dep_)

    return G

def get_type(token):
    if token.dep_ == "ROOT":
        return "root"
    elif token.pos_ == "VERB":
        return "verb"
    elif token.pos_ == "ADJ":
        return "adj"
    return "noun"
