import os
from pathlib import Path

from dash import Dash, callback_context, html, dcc, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


app = Dash(__name__, title='Dash File Explorer', external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css"),
    html.A(
        "Fork me on Github",
        className="github-fork-ribbon",
        href="https://github.com/eliasdabbas/dash-file-browser",
        title="Fork me on GitHub", **{"data-ribbon": "Fork me on GitHub"}),
    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(lg=1, sm=1, md=1),
        dbc.Col([
            dcc.Store(id='stored_cwd', data=os.getcwd()),
            html.H1('Dash File Browser'),
            html.Hr(), html.Br(), html.Br(), html.Br(),
            html.H5(html.B(html.A("⬆️ Parent directory", href='#', id='parent_dir'))),
            html.H3([html.Code(os.getcwd(), id='cwd')]),
                    html.Br(), html.Br(),
            html.Div(id='cwd_files'), 
        ], lg=10, sm=11, md=10)
    ])
])


@app.callback(
    Output("cwd", 'children'),
    Input('stored_cwd', 'data'),
    Input('parent_dir', 'n_clicks'),
    Input("cwd", 'children'),
    prevent_initial_call=True)
def get_parent_directory(stored_cwd, n_clicks, currentdir):
    triggered_id = callback_context.triggered_id
    if triggered_id == 'stored_cwd':
        return stored_cwd
    parent = Path(currentdir).parent.as_posix()
    return parent


@app.callback(
    Output('cwd_files', 'children'),
    Input('cwd', 'children'))
def list_cwd_files(cwd):
    path = Path(cwd)
    cwd_files = []
    if path.is_dir():
        files = sorted(os.listdir(path), key=str.lower)
        for i, file in enumerate(files):
            filepath = Path(file)
            full_path=os.path.join(cwd, filepath.as_posix())
            is_dir = Path(full_path).is_dir()
            link = html.A([
                html.Span(
                file, id={'type': 'listed_file', 'index': i},
                title=full_path,
                style={'fontWeight': 'bold'} if is_dir else {}
            )], href='#')
            prepend = '' if not is_dir else '📂'
            cwd_files.append(prepend)
            cwd_files.append(link)
            cwd_files.append(html.Br())
    return cwd_files


@app.callback(
    Output('stored_cwd', 'data'),
    Input({'type': 'listed_file', 'index': ALL}, 'n_clicks'),
    State({'type': 'listed_file', 'index': ALL}, 'children'),
    State({'type': 'listed_file', 'index': ALL}, 'title'),
    State('cwd', 'children'))
def store_clicked_file(n_clicks, href, title, cwd):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    ctx = callback_context
    index = ctx.triggered_id['index']
    return title[index]

if __name__ == '__main__':
    app.run_server(debug=True)
