# app.py
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import spacy
import networkx as nx
import dash_daq as daq
import base64
import io
import plotly.io as pio
from PIL import Image

from mindmap_generator import build_mindmap

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

app = dash.Dash(__name__)
server = app.server

app.title = "MindMap AI"

# Initial theme
theme_dark = {
    'background': '#111111',
    'text': '#FFFFFF',
    'node_text': 'white'
}
theme_light = {
    'background': '#FFFFFF',
    'text': '#000000',
    'node_text': 'black'
}

app.layout = html.Div([
    dcc.Store(id='theme-store', data='dark'),
    html.Button("🌙 Switch to Light Mode", id='theme-toggle', n_clicks=0),
    html.H1("\U0001F9E0 MindMap AI Generator", id='title', style={'textAlign': 'center'}),
    dcc.Input(id='input-text', type='text', placeholder='Enter your topic or idea', style={'width': '60%'}),
    dcc.Dropdown(
        id='layout-style',
        options=[
            {'label': 'Breadthfirst', 'value': 'breadthfirst'},
            {'label': 'Circle', 'value': 'circle'},
            {'label': 'Grid', 'value': 'grid'},
            {'label': 'Cose', 'value': 'cose'}
        ],
        value='breadthfirst',
        style={'width': '200px'}
    ),
    html.Button('Generate Map', id='generate-button'),
    html.Button('Download PNG', id='download-button'),
    html.Div(id='download-status'),
    cyto.Cytoscape(
        id='mindmap',
        layout={},  # Layout will be set by callback
        style={'width': '100%', 'height': '600px'},
        elements=[],
        stylesheet=[]
    )
], id='main-div')


@app.callback(
    Output('mindmap', 'elements'),
    Output('mindmap', 'stylesheet'),
    Input('generate-button', 'n_clicks'),
    State('input-text', 'value'),
    State('theme-store', 'data')
)
def update_mindmap(n_clicks, text, theme):
    if not text:
        return [], []

    G = build_mindmap(text)

    elements = []
    for node in G.nodes:
        elements.append({"data": {"id": node, "label": node}})
    for source, target in G.edges:
        elements.append({"data": {"source": source, "target": target}})

    node_text_color = theme_dark['node_text'] if theme == 'dark' else theme_light['node_text']

    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'label': 'data(label)',
                'color': node_text_color,
                'background-color': '#0074D9',
                'text-outline-color': '#0074D9',
                'text-outline-width': 2,
                'font-size': 16
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': 'gray',
                'width': 2
            }
        }
    ]

    return elements, stylesheet


@app.callback(
    Output('mindmap', 'layout'),
    Input('layout-style', 'value')
)
def update_layout(layout_value):
    return {'name': layout_value}


@app.callback(
    Output('main-div', 'style'),
    Output('title', 'style'),
    Output('theme-store', 'data'),
    Output('theme-toggle', 'children'),
    Input('theme-toggle', 'n_clicks'),
    State('theme-store', 'data')
)
def toggle_theme(n_clicks, current):
    if n_clicks % 2 == 0:
        return theme_dark, {'color': theme_dark['text'], 'textAlign': 'center'}, 'dark', '🌙 Switch to Light Mode'
    else:
        return theme_light, {'color': theme_light['text'], 'textAlign': 'center'}, 'light', '☀️ Switch to Dark Mode'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
