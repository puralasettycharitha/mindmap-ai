import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import dash_daq as daq
import base64
from PIL import Image
import io
from mindmap_generator import build_mindmap

cyto.load_extra_layouts()
app = dash.Dash(__name__)
server = app.server

# Theme state
app.layout = html.Div([
    daq.ToggleSwitch(id="theme-toggle", label=["🌞 Light", "🌚 Dark"], value=True),
    html.H1("🧠 MindMap AI Generator", className="title"),
    dcc.Input(id="user-input", type="text", placeholder="Enter a concept...", className="input-box"),
    dcc.Dropdown(
        id='layout-dropdown',
        options=[
            {'label': 'Breadthfirst', 'value': 'breadthfirst'},
            {'label': 'Circle', 'value': 'circle'},
            {'label': 'Grid', 'value': 'grid'},
            {'label': 'Cose', 'value': 'cose'}
        ],
        value='breadthfirst',
        className="dropdown"
    ),
    html.Div([
        html.Button("Generate Map", id="generate-btn", className="btn"),
        html.Button("Download PNG", id="download-btn", className="btn")
    ], className="button-group"),
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name': 'breadthfirst'},
        style={'width': '100%', 'height': '600px'},
        elements=[]
    ),
    dcc.Download(id="download-image")
], id="main-container", className="dark")  # default dark theme


@app.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'layout'),
    Input('generate-btn', 'n_clicks'),
    State('user-input', 'value'),
    State('layout-dropdown', 'value'),
    prevent_initial_call=True
)
def generate_map(n_clicks, user_input, layout_style):
    if not user_input:
        return [], {'name': layout_style}
    elements = build_mindmap(user_input)
    return elements, {'name': layout_style}


@app.callback(
    Output("main-container", "className"),
    Input("theme-toggle", "value")
)
def toggle_theme(dark_mode):
    return "dark" if dark_mode else "light"


@app.callback(
    Output("download-image", "data"),
    Input("download-btn", "n_clicks"),
    State("cytoscape", "elements"),
    prevent_initial_call=True
)
def download_as_png(n_clicks, elements):
    from dash_cytoscape.utils import to_image
    image_bytes = to_image(elements, format="png")
    return dcc.send_bytes(image_bytes, "mindmap.png")


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)
