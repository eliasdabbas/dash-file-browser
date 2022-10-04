import os
from pathlib import Path

from dash import Dash, callback_context, html, dcc, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


folder_icon = '📂'
file_idon = '📄'

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div([
    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dcc.Store(id='stored_cwd', data=os.getcwd()),
            html.H1('Dash File Browser'), html.Br(), html.Br(),
            html.H5(html.B(html.A("⬆️ Parent directory", href='#', id='parent_dir'))),
            html.H3([html.Code(os.getcwd(), id='cwd')]),
                    html.Br(), html.Br(),
            html.Div(id='cwd_files'), 
        ])
    ])
])


@app.callback(
    Output("cwd", 'children'),
    Input('stored_cwd', 'modified_timestamp'),
    Input('stored_cwd', 'data'),
    Input('parent_dir', 'n_clicks'),
    Input("cwd", 'children'),
    prevent_initial_call=True)
def get_parent_directory(timestamp, stored_cwd, n_clicks, currentdir):
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
        files = sorted(os.listdir(path))
        for i, file in enumerate(files):
            filepath = Path(file)
            title=os.path.join(cwd, filepath.as_posix())
            is_dir = Path(title).is_dir()
            link = html.A([html.Span(
                file, id={'type': 'listed_file', 'index': i},
                title=title,
                style={'fontWeight': 'bold'} if is_dir else {}
            )], href='#')
            prepend = '' if not is_dir else folder_icon
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
def display_clicked_file(n_clicks, href, title, cwd):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    ctx = callback_context
    index = ctx.triggered_id['index']
    path = os.path.join(cwd, href[index])
    return title[index]

if __name__ == '__main__':
    app.run_server(debug=True)
