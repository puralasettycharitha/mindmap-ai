import os
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
from mindmap_generator import build_mindmap

app = dash.Dash(__name__)
server = app.server  # for deployment

app.layout = html.Div([
    dcc.Store(id='theme-store', data='dark'),
    html.Button("🌙 Switch to Light Mode", id='theme-toggle', n_clicks=0),

    html.Div(id='page-content', children=[
        html.H1("🧠 MindMap AI Generator", id='title'),
        dcc.Input(id='input-text', type='text', placeholder='Enter a concept...', style={'width': '80%'}),
        html.Button("Generate Map", id='generate-button'),
        html.Button("Download PNG", id='download-button'),
        dcc.Input(id='layout-style', type='text', value='breadthfirst'),
        cyto.Cytoscape(
            id='mindmap',
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '600px'},
            elements=[]
        ),
        html.Div(id='download-link')
    ])
], id='main-container', style={'backgroundColor': '#111', 'color': 'white', 'padding': '20px'})

@app.callback(
    Output('main-container', 'style'),
    Output('title', 'style'),
    Output('theme-toggle', 'children'),
    Input('theme-toggle', 'n_clicks')
)
def toggle_theme(n_clicks):
    if n_clicks % 2 == 0:
        return (
            {'backgroundColor': '#111', 'color': 'white', 'padding': '20px'},
            {'color': 'white'},
            '🌙 Switch to Light Mode'
        )
    else:
        return (
            {'backgroundColor': '#fff', 'color': 'black', 'padding': '20px'},
            {'color': 'black'},
            '☀️ Switch to Dark Mode'
        )

@app.callback(
    Output('mindmap', 'elements'),
    Input('generate-button', 'n_clicks'),
    State('input-text', 'value'),
    State('layout-style', 'value'),
    prevent_initial_call=True
)
def generate_mindmap(n_clicks, input_text, layout):
    G = build_mindmap(input_text)
    nodes = [{'data': {'id': n, 'label': n}} for n in G.nodes()]
    edges = [{'data': {'source': u, 'target': v}} for u, v in G.edges()]
    return nodes + edges

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
