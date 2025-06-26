import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_cytoscape as cyto
import json
import base64
from mindmap_generator import build_mindmap
import os

app = dash.Dash(__name__)
server = app.server

layout_options = [
    {'label': 'Breadthfirst (Tree)', 'value': 'breadthfirst'},
    {'label': 'Grid', 'value': 'grid'},
    {'label': 'Circle', 'value': 'circle'},
    {'label': 'Cose (Auto Layout)', 'value': 'cose'},
    {'label': 'Preset (Manual Drag)', 'value': 'preset'}
]

app.layout = html.Div([
    html.H1("\U0001F9E0 MindMap AI", style={'textAlign': 'center'}),

    html.Div([
        html.P("Enter your problem statement or idea:"),
        dcc.Textarea(
            id='input-text',
            placeholder='e.g., Build a delivery app with tracking and payment...',
            style={'width': '100%', 'height': 150}
        ),
        html.Br(),

        html.Div([
            html.Button("Generate Mind Map", id='generate-btn', n_clicks=0),
            html.Button("Export JSON", id='export-btn', n_clicks=0, style={'marginLeft': '10px'}),
            html.Button("Export PNG", id='png-btn', n_clicks=0, style={'marginLeft': '10px'}),
            dcc.Upload(
                id='upload-json',
                children=html.Button('Upload JSON', style={'marginLeft': '10px'}),
                multiple=False
            ),
            dcc.Download(id="download-json"),
        ]),

        html.Br(),

        html.Div([
            html.Label("Choose Layout:"),
            dcc.Dropdown(
                id='layout-dropdown',
                options=layout_options,
                value='breadthfirst',
                clearable=False,
                style={'width': '300px', 'margin': 'auto'}
            )
        ])
    ], style={'textAlign': 'center'}),

    html.Br(),

    dcc.Store(id='trigger-png-store'),
    dcc.Store(id='png-trigger-store'),

    cyto.Cytoscape(
        id='mindmap',
        layout={'name': 'breadthfirst'},
        style={'width': '100%', 'height': '600px'},
        elements=[],
        userZoomingEnabled=True,
        userPanningEnabled=True,
        boxSelectionEnabled=True,
        stylesheet=[
            {'selector': 'node[type = "root"]', 'style': {'background-color': '#ff4136'}},
            {'selector': 'node[type = "noun"]', 'style': {'background-color': '#0074D9'}},
            {'selector': 'node[type = "verb"]', 'style': {'background-color': '#2ECC40'}},
            {'selector': 'node[type = "adj"]', 'style': {'background-color': '#FFDC00'}},
            {'selector': 'node', 'style': {
                'content': 'data(label)',
                'color': 'white',
                'font-size': '20px',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': 'label',
                'height': 'label'
            }},
            {'selector': 'edge', 'style': {
                'line-color': '#555',
                'target-arrow-shape': 'triangle',
                'target-arrow-color': '#555',
                'label': 'data(label)',
                'font-size': '12px',
                'text-background-color': '#fff',
                'text-background-opacity': 1
            }}
        ]
    )
])

@app.callback(
    Output('mindmap', 'elements'),
    Input('generate-btn', 'n_clicks'),
    Input('upload-json', 'contents'),
    State('input-text', 'value')
)
def update_mindmap_or_upload(n_clicks, uploaded_contents, text):
    triggered_id = ctx.triggered_id

    if triggered_id == 'generate-btn' and text:
        G = build_mindmap(text)
        nodes = [{'data': {
                    'id': node,
                    'label': node,
                    'type': G.nodes[node].get('type', 'noun')},
                  'position': {'x': 0, 'y': 0}}
                 for node in G.nodes() if node.strip()]
        edges = [{'data': {
                    'source': src,
                    'target': tgt,
                    'label': data.get("label", "")}}
                 for src, tgt, data in G.edges(data=True) if src.strip() and tgt.strip()]
        return nodes + edges

    elif triggered_id == 'upload-json' and uploaded_contents:
        try:
            content_type, content_string = uploaded_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')
            elements = json.loads(decoded)
            return elements
        except Exception:
            return []

    return []

@app.callback(
    Output("download-json", "data"),
    Input("export-btn", "n_clicks"),
    State("mindmap", "elements"),
    prevent_initial_call=True
)
def export_mindmap(n, elements):
    if not elements:
        return dash.no_update
    return dcc.send_string(json.dumps(elements, indent=2), filename="mindmap.json")

@app.callback(
    Output('mindmap', 'layout'),
    Input('layout-dropdown', 'value')
)
def update_layout(selected_layout):
    return {'name': selected_layout}

@app.callback(
    Output("trigger-png-store", "data"),
    Input("png-btn", "n_clicks"),
    prevent_initial_call=True
)
def export_png(n):
    return {"trigger": True}

app.clientside_callback(
    """
    function(data) {
        if (!data || !window.cy) return;
        window.cy.png({
            full: true,
            output: 'blob'
        }).then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mindmap.png';
            a.click();
            URL.revokeObjectURL(url);
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output("png-trigger-store", "data"),
    Input("trigger-png-store", "data")
)

app.index_string = app.index_string.replace(
    "</head>",
    "<script>document.addEventListener('DOMContentLoaded', function(){window.cy = null;});</script></head>"
)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=True, host='0.0.0.0', port=port)

