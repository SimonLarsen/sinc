import os
import glob
import argparse
from natsort import natsorted
from pathlib import Path
from math import ceil
from typing import List
from dash import Dash, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import flask
from layout import make_filter_column, create_layout


IMAGES_FOLDER = None


def get_filter_matches(filter: str) -> List[str]:
    full_filter = str(IMAGES_FOLDER / filter)
    files = [path for path in glob.glob(full_filter) if os.path.isfile(path)]
    files = natsorted(files)
    return files


app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    external_stylesheets=[
        dbc.themes.ZEPHYR,
        dbc.icons.BOOTSTRAP
    ]
)

app.layout = create_layout(app)
app.title = "sinc"


@app.callback(
    Output("filters", "children"),
    Input("num_columns", "value"),
    State("filters", "children"),
)
def update_filter_controls(num_columns, gallery):
    if num_columns < len(gallery):
        gallery = gallery[:num_columns]
    else:
        while len(gallery) < num_columns:
            new_column = make_filter_column(len(gallery))
            gallery.append(new_column)
    return gallery


@app.callback(
    Output("file_matches", "data"),
    Output({"type": "num_images", "index": ALL}, "children"),
    Input({"type": "filter", "index": ALL}, "value"),
    Input("refresh_button", "n_clicks")
)
def update_file_matches(filters: List[str], refresh_clicks: int):
    matches = [
        get_filter_matches(filter) if filter is not None else []
        for filter in filters
    ]
    num_texts = [f"{len(f)} results" for f in matches]
    return matches, num_texts


@app.callback(
    Output("pagination", "max_value"),
    Input("file_matches", "data"),
    Input("num_per_page", "value")
)
def update_pagination(file_matches: List[str], num_per_page: int):
    file_counts = [len(x) for x in file_matches]
    max_files = max(file_counts)
    return max(ceil(max_files / num_per_page), 1)


@app.callback(
    Output("images", "children"),
    Input("file_matches", "data"),
    Input("pagination", "active_page"),
    Input("num_per_page", "value")
)
def update_images(
    file_matches: List[str],
    active_page: int,
    num_per_page: int
):
    i_start = (active_page - 1) * num_per_page
    i_end = i_start + num_per_page

    paths = [f[i_start:i_end] for f in file_matches]
    num_rows = max(map(len, paths))

    output = []
    for row in range(num_rows):
        cols = []
        for col in range(len(file_matches)):
            if row < len(paths[col]):
                img_src = "/images/" + os.path.relpath(paths[col][row], IMAGES_FOLDER)
                elem = html.Figure(
                    className="figure",
                    children=[
                        html.Figcaption(paths[col][row], className="figure-caption"),
                        html.Img(src=img_src, className="figure-img img-fluid")
                    ]
                )
            else:
                elem = html.Div()
            cols.append(dbc.Col(elem))
        output.append(dbc.Row(cols))
    return output


app.clientside_callback(
    """
    function(active_page) {
        var cont = document.getElementById("gallery_container");
        cont.scrollTo(0, 0);
        return active_page;
    }
    """,
    Output("pagination", "active_page"),
    Input("pagination", "active_page")
)


@app.server.route("/images/<path:filename>")
def get_image(filename):
    return flask.send_from_directory(
        directory=IMAGES_FOLDER,
        path=filename
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()

    IMAGES_FOLDER = args.folder

    app.run_server(debug=True)
