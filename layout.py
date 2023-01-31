from dash import html, dcc
import dash_bootstrap_components as dbc


def make_filter_column(index: int):
    filter = dbc.Input(
        id={"type": "filter", "index": index},
        type="text",
        placeholder="Filter e.g. \"output_*.jpg\""
    )

    counter = dbc.Label(
        id={"type": "num_images", "index": index},
        children="0 results",
        width="auto"
    )

    return dbc.Col(
        dbc.Row(
            [
                dbc.Col(filter),
                dbc.Col(counter)
            ]
        )
    )


def create_layout(app):
    sidebar_logo = html.A(
        className="d-flex align-items-center justify-content-center text-white text-decoration-none",
        children=[
            html.Img(
                src=app.get_asset_url("icon.png"),
                width=32,
                className="me-2"
            ),
            html.Span(
                "sinc",
                className="fs-4"
            )
        ]
    )

    sidebar = html.Div(
        className="p-3",
        children=[
            sidebar_logo,
            html.Hr(),
            dbc.Label("Columns", html_for="num_columns"),
            dbc.Input(
                id="num_columns",
                type="number",
                value=2,
                min=1,
                max=8,
                step=1,
                className="mb-3"
            ),
            dbc.Label("Images per page", html_for="num_per_page"),
            dcc.Dropdown(
                id="num_per_page",
                options=[{"label": str(i), "value": i} for i in [10, 20, 50, 100]],
                value=10,
                className="mb-3"
            ),
            dbc.Button(
                id="refresh_button",
                children=[
                    html.I(className="bi bi-arrow-clockwise me-2"),
                    "Refresh",
                ],
                className="mb-auto"
            )
        ]
    )

    gallery = dbc.Container(
        id="gallery_container",
        fluid=True,
        className="p-3 overflow-auto h-100",
        children=[
            dbc.Row(
                id="filters",
                className="mb-3",
                children=[make_filter_column(0), make_filter_column(1)]
            ),
            html.Div(id="images"),
            html.Div(
                dbc.Pagination(id="pagination", max_value=1, active_page=1, first_last=True, previous_next=True),
                className="d-flex justify-content-center"
            )
        ]
    )

    layout = html.Div(
        [
            html.Main(
                className="d-flex flex-nowrap",
                style={"height": "100vh"},
                children=[
                    html.Div(
                        sidebar,
                        className="d-flex flex-column flex-shrink-0 text-bg-dark",
                        style={"width": "220px"}
                    ),
                    html.Div(
                        gallery,
                        className="d-flex flex-grow-1"
                    )
                ]
            ),
            dcc.Store(id="file_matches")
        ]
    )

    return layout