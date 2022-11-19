import datetime
import os
from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, Dash, Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from icons import icons


def icon_file(extension, width=24, height=24):
    """Retrun an html.img of the svg icon for a given extension."""
    filetype = icons.get(extension)
    file_name = f'file_type_{filetype}.svg' if filetype is not None else 'default_file.svg'
    html_tag = html.Img(src=app.get_asset_url(f'icons/{file_name}'),
                        width=width, height=height)
    return html_tag


def nowtimestamp(timestamp, fmt='%b %d, %Y %H:%M'):
    return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)


def file_info(path):
    """Get file info for a given path.

    Uncomment the attributes that you want to display.

    Parameters:
    -----------
    path : pathlib.Path object
    """
    file_stat = path.stat()
    d = {
        'extension': path.suffix if not path.name.startswith('.') else path.name,
        'filename': path.name,
        # 'fullpath': str(path.absolute()),
        'size': format(file_stat.st_size, ','),
        'created': nowtimestamp(file_stat.st_ctime),
        'modified': nowtimestamp(file_stat.st_mtime),
        # 'accessed': nowtimestamp(file_stat.st_atime),
        # 'is_dir': str(path.is_dir()),
        # 'is_file': str(path.is_file()),
    }
    return d


app = Dash(
    __name__,
    title='Dash File Browser',
    assets_folder='assets',
    meta_tags=[
        {'name': 'description',
         'content': """Dash File Browser - a simple browser for files that is \
used to explore files and folder on the server. This is useful if your users \
need to manipulate and analyze files on the server."""},
        ],
    external_stylesheets=[dbc.themes.FLATLY])

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
            html.H5(html.B(html.A("⬆️ Parent directory", href='#',
                                  id='parent_dir'))),
            html.H3([html.Code(os.getcwd(), id='cwd')]),
                    html.Br(), html.Br(),
            html.Div(id='cwd_files',
                     style={'height': 500, 'overflow': 'scroll'}),
        ], lg=10, sm=11, md=10)
    ])
] + [html.Br() for _ in range(15)])


@app.callback(
    Output('cwd', 'children'),
    Input('stored_cwd', 'data'),
    Input('parent_dir', 'n_clicks'),
    Input('cwd', 'children'),
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
    all_file_details = []
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
                style={'fontWeight': 'bold', 'fontSize': 18} if is_dir else {}
            )], href='#')
            details = file_info(Path(full_path))
            details['filename'] = link
            if is_dir:
                details['extension'] = html.Img(
                    src=app.get_asset_url('icons/default_folder.svg'),
                    width=25, height=25)
            else:
                details['extension'] = icon_file(details['extension'][1:])
            all_file_details.append(details)

    df = pd.DataFrame(all_file_details)
    df = df.rename(columns={"extension": ''})
    table = dbc.Table.from_dataframe(df, striped=False, bordered=False,
                                     hover=True, size='sm')
    return html.Div(table)


@app.callback(
    Output('stored_cwd', 'data'),
    Input({'type': 'listed_file', 'index': ALL}, 'n_clicks'),
    State({'type': 'listed_file', 'index': ALL}, 'title'))
def store_clicked_file(n_clicks, title):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    ctx = callback_context
    index = ctx.triggered_id['index']
    return title[index]

if __name__ == '__main__':
    app.run_server(debug=True)
