import os
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
from mindmap_generator import build_mindmap

# Initialize Dash
app = dash.Dash(__name__)
server = app.server  # for deployment (Render)

# Layout
app.layout = html.Div([
    dcc.Store(id='theme-store', data='dark'),

    # Theme toggle
    html.Button("🌙 Switch to Light Mode", id='theme-toggle', n_clicks=0),

    html.Div(id='page-content', children=[
        html.H1("🧠 MindMap AI Generator", id='title'),

        dcc.Input(
            id='input-text',
            type='text',
            placeholder='Enter a concept...',
            style={'width': '80%', 'padding': '10px'}
        ),
        html.Button("Generate Map", id='generate-button', style={'margin': '10px'}),
        html.Button("Download PNG", id='download-button'),

        dcc.Dropdown(
            id='layout-style',
            options=[
                {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                {'label': 'Circle', 'value': 'circle'},
                {'label': 'Grid', 'value': 'grid'},
                {'label': 'Cose', 'value': 'cose'}
            ],
            value='breadthfirst',
            clearable=False,
            style={'width': '200px', 'margin': '10px'}
        ),

        cyto.Cytoscape(
            id='mindmap',
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '600px'},
            elements=[]
        ),

        html.Div(id='download-link')
    ])
], id='main-container', style={'backgroundColor': '#111', 'color': 'white', 'padding': '20px'})


# 🔄 Theme Toggle Callback
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


# 🧠 Mind Map Generator
@app.callback(
    Output('mindmap', 'elements'),
    Input('generate-button', 'n_clicks'),
    State('input-text', 'value'),
    prevent_initial_call=True
)
def generate_mindmap(n_clicks, input_text):
    G = build_mindmap(input_text)
    nodes = [{'data': {'id': n, 'label': n}} for n in G.nodes()]
    edges = [{'data': {'source': u, 'target': v}} for u, v in G.edges()]
    return nodes + edges


# 🔄 Layout Update Callback
@app.callback(
    Output('mindmap', 'layout'),
    Input('layout-style', 'value')
)
def update_layout(layout_name):
    return {'name': layout_name}


# ✅ Run Server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host='0.0.0.0', port=port)
