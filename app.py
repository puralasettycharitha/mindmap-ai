import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
import base64
import io
from PIL import Image
import dash_daq as daq

from mindmap_generator import build_mindmap

app = dash.Dash(__name__)
server = app.server

dark_theme = {
    "background": "#111111",
    "text": "#FFFFFF"
}
light_theme = {
    "background": "#FFFFFF",
    "text": "#000000"
}

app.layout = html.Div(
    id="main-container",
    style={"backgroundColor": dark_theme["background"], "color": dark_theme["text"], "minHeight": "100vh", "padding": "20px"},
    children=[
        daq.ToggleSwitch(id='theme-toggle', label=['🌙 Dark', '☀️ Light'], value=True),

        html.H1("🧠 MindMap AI Generator", style={"textAlign": "center"}),

        dcc.Input(id="input-text", type="text", placeholder="Enter your idea or topic...", style={"width": "100%", "padding": "10px"}),

        html.Div([
            dcc.Dropdown(
                id="layout-dropdown",
                options=[{"label": layout, "value": layout.lower()} for layout in ["Breadthfirst", "Circle", "Grid", "Cose"]],
                value="breadthfirst",
                style={"width": "200px", "marginTop": "10px"}
            ),
            html.Button("Generate Map", id="generate-button", n_clicks=0, style={"marginLeft": "10px"}),
            html.Button("Download PNG", id="download-button", n_clicks=0, style={"marginLeft": "10px"}),
        ], style={"display": "flex", "alignItems": "center", "marginTop": "10px"}),

        html.Div(id="cytoscape-container", children=[
            cyto.Cytoscape(
                id="mindmap",
                layout={"name": "breadthfirst"},
                style={"width": "100%", "height": "600px"},
                elements=[],
                stylesheet=[
                    {"selector": "node", "style": {"content": "data(label)", "text-valign": "center", "color": "#fff", "background-color": "#0074D9"}},
                    {"selector": "edge", "style": {"line-color": "#ccc", "width": 2}},
                ]
            )
        ])
    ]
)


@app.callback(
    Output("mindmap", "elements"),
    Output("mindmap", "layout"),
    Input("generate-button", "n_clicks"),
    State("input-text", "value"),
    State("layout-dropdown", "value")
)
def update_mindmap(n_clicks, input_text, layout_value):
    if not input_text:
        return [], {"name": layout_value}

    G = build_mindmap(input_text)

    nodes = [{"data": {"id": str(node), "label": str(node)}} for node in G.nodes()]
    edges = [{"data": {"source": str(src), "target": str(dst)}} for src, dst in G.edges()]

    return nodes + edges, {"name": layout_value}


@app.callback(
    Output("main-container", "style"),
    Input("theme-toggle", "value")
)
def toggle_theme(is_dark):
    theme = dark_theme if is_dark else light_theme
    return {"backgroundColor": theme["background"], "color": theme["text"], "minHeight": "100vh", "padding": "20px"}


if __name__ == "__main__":
    app.run()
