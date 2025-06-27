import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import openai
import networkx as nx
import os

# 🔐 Set your OpenAI API key
openai.api_key = "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Replace with your key

# 🌟 Initialize Dash
app = dash.Dash(__name__)
server = app.server

# 🌐 Use GPT to extract keywords for mind map
def extract_keywords(text):
    try:
        prompt = f"Generate 8-10 keywords or nodes for a mind map based on: {text}. Return them as a semicolon-separated list."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mind map assistant. Return only keywords separated by semicolons."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        content = response['choices'][0]['message']['content']
        return [kw.strip() for kw in content.split(';') if kw.strip()]
    except Exception as e:
        return ["Error", str(e)]

# 📌 Build a graph using NetworkX
def build_graph(text):
    keywords = extract_keywords(text)
    G = nx.Graph()
    G.add_node("ROOT", label=text)

    for kw in keywords:
        G.add_node(kw, label=kw)
        G.add_edge("ROOT", kw)

    elements = []
    for node, data in G.nodes(data=True):
        elements.append({'data': {'id': node, 'label': data.get('label', node)}})
    for source, target in G.edges():
        elements.append({'data': {'source': source, 'target': target}})
    return elements

# 🎨 Dark theme stylesheet
def get_stylesheet():
    return [
        {
            'selector': 'node',
            'style': {
                'content': 'data(label)',
                'background-color': '#1f77b4',
                'color': '#ffffff',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-size': '14px',
                'width': '60px',
                'height': '60px',
                'border-width': 2,
                'border-color': '#444'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': '#999',
                'width': 2
            }
        }
    ]

# 🌐 Layout
app.layout = html.Div(
    style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'},
    children=[
        html.H1("🧠 MindMap AI Generator", style={'textAlign': 'center'}),

        dcc.Input(
            id='input-text',
            type='text',
            placeholder='Enter your idea or problem statement...',
            style={'width': '80%', 'padding': '10px', 'fontSize': '16px', 'marginBottom': '10px'}
        ),

        html.Div([
            html.Button('Generate Map', id='generate-button', n_clicks=0, style={'marginRight': '10px'}),
            html.Button('Download PNG', id='download-button', n_clicks=0, style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='layout-dropdown',
                options=[
                    {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                    {'label': 'Circle', 'value': 'circle'},
                    {'label': 'Grid', 'value': 'grid'},
                    {'label': 'Concentric', 'value': 'concentric'},
                    {'label': 'Cose (Organic)', 'value': 'cose'}
                ],
                value='breadthfirst',
                style={'width': '300px', 'display': 'inline-block', 'marginTop': '10px'}
            )
        ], style={'marginBottom': '10px'}),

        cyto.Cytoscape(
            id='cytoscape',
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '600px'},
            elements=[],
            stylesheet=get_stylesheet()
        )
    ]
)

# 🔁 Callback: update graph
@app.callback(
    Output('cytoscape', 'elements'),
    Input('generate-button', 'n_clicks'),
    State('input-text', 'value'),
    prevent_initial_call=True
)
def update_mindmap(n_clicks, text):
    if not text:
        return []
    return build_graph(text)

# 🔁 Callback: change layout
@app.callback(
    Output('cytoscape', 'layout'),
    Input('layout-dropdown', 'value')
)
def change_layout(layout_name):
    return {'name': layout_name}

# 🔁 Callback: export PNG
@app.callback(
    Output('cytoscape', 'generateImage'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def download_png(n_clicks):
    return {
        'type': 'png',
        'action': 'download',
        'scale': 2
    }

# 🚀 Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)