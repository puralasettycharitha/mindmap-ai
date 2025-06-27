# 🔧 app.py

import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
import json
import os
from mindmap_generator import build_mindmap

app = dash.Dash(__name__)
server = app.server

# Color styles for POS types - default light
light_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'color': 'black',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'text-wrap': 'wrap',
            'width': 'label',
            'height': 'label'
        }
    },
    {
        'selector': '.noun',
        'style': {'background-color': '#3498db'}
    },
    {
        'selector': '.verb',
        'style': {'background-color': '#2ecc71'}
    },
    {
        'selector': '.adj',
        'style': {'background-color': '#f39c12'}
    },
    {
        'selector': '.root',
        'style': {'background-color': '#e74c3c'}
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#666',
            'target-arrow-color': '#666',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 1,
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
        }
    },
]

dark_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'color': 'white',
            'background-color': '#444',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'text-wrap': 'wrap',
            'width': 'label',
            'height': 'label'
        }
    },
    {
        'selector': '.noun',
        'style': {'background-color': '#2980b9'}
    },
    {
        'selector': '.verb',
        'style': {'background-color': '#27ae60'}
    },
    {
        'selector': '.adj',
        'style': {'background-color': '#d35400'}
    },
    {
        'selector': '.root',
        'style': {'background-color': '#c0392b'}
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#aaa',
            'target-arrow-color': '#aaa',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 1,
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
        }
    },
]

# Layout options
layout_options = [
    {'label': 'Breadthfirst', 'value': 'breadthfirst'},
    {'label': 'Circle', 'value': 'circle'},
    {'label': 'Grid', 'value': 'grid'},
    {'label': 'Concentric', 'value': 'concentric'}
]

app.layout = html.Div([
    html.H1("🧠 MindMap AI - Auto Sketch Your Thinking"),
    dcc.Textarea(id='input-text', placeholder='Enter your idea...', style={'width': '100%', 'height': 100}),
    html.Button('Generate Mind Map', id='generate-btn', n_clicks=0),
    dcc.Dropdown(
        id='layout-selector',
        options=layout_options,
        value='breadthfirst',
        style={'margin-top': '10px'}
    ),
    dcc.RadioItems(
        id='theme-toggle',
        options=[
            {'label': '🌞 Light', 'value': 'light'},
            {'label': '🌚 Dark', 'value': 'dark'}
        ],
        value='light',
        labelStyle={'display': 'inline-block', 'margin-right': '15px'}
    ),
    html.Div(id='cytoscape-container'),
    dcc.Download(id='download-json'),
    html.Button("Export JSON", id="export-json"),
    dcc.Upload(
        id='upload-json',
        children=html.Div(['📤 Drag or Select JSON File']),
        style={'width': '100%', 'padding': '10px', 'border': '1px dashed black'},
        multiple=False
    ),
])

@app.callback(
    Output('cytoscape-container', 'children'),
    Input('generate-btn', 'n_clicks'),
    State('input-text', 'value'),
    State('layout-selector', 'value'),
    State('theme-toggle', 'value')
)
def update_mindmap(n_clicks, text, layout, theme):
    if not text:
        return html.Div("Please enter some text.")

    G = build_mindmap(text)
    elements = []
    for node, data in G.nodes(data=True):
        node_type = data.get("type", "noun")
        tooltip = data.get("tooltip", "")
        elements.append({
            'data': {'id': node, 'label': f"{node}\n({tooltip})"},
            'classes': node_type
        })

    for source, target, data in G.edges(data=True):
        elements.append({
            'data': {
                'source': source,
                'target': target,
                'label': data.get('label', '')
            }
        })

    current_stylesheet = light_stylesheet if theme == 'light' else dark_stylesheet

    return cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={'name': layout},
        style={'width': '100%', 'height': '600px'},
        stylesheet=current_stylesheet
    )

@app.callback(
    Output("download-json", "data"),
    Input("export-json", "n_clicks"),
    State("input-text", "value"),
    prevent_initial_call=True
)
def export_json(n_clicks, text):
    G = build_mindmap(text)
    data = nx.node_link_data(G)
    return dict(content=json.dumps(data, indent=2), filename="mindmap.json")

@app.callback(
    Output("input-text", "value"),
    Input("upload-json", "contents"),
    prevent_initial_call=True
)
def upload_json(contents):
    import base64
    content_type, content_string = contents.split(',')
    decoded = json.loads(base64.b64decode(content_string).decode('utf-8'))
    G = nx.node_link_graph(decoded)
    return "Loaded mindmap with {} nodes.".format(len(G.nodes))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)