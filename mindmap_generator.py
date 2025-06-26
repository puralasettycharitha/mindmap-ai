import spacy
import networkx as nx

nlp = spacy.load("en_core_web_sm")

def build_mindmap(text):
    doc = nlp(text)
    G = nx.DiGraph()

    for sent in doc.sents:
        for token in sent:
            if not token.is_alpha or token.is_stop:
                continue

            token_type = "noun"
            if token.pos_ == "VERB":
                token_type = "verb"
            elif token.pos_ == "ADJ":
                token_type = "adj"
            elif token.dep_ == "ROOT":
                token_type = "root"

            G.add_node(token.text, type=token_type)

            # Connect child to head
            if token.head != token and token.head.is_alpha:
                G.add_node(token.head.text, type=guess_type(token.head))
                G.add_edge(token.head.text, token.text, label=token.dep_)

    return G

def guess_type(token):
    if token.pos_ == "VERB":
        return "verb"
    elif token.pos_ == "ADJ":
        return "adj"
    elif token.dep_ == "ROOT":
        return "root"
    return "noun"
