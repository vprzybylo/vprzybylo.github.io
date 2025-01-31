"""Set up the app layout"""

import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
import globals
from dash import dcc, html


def content():

    storage = "session"
    return html.Div(
        id="page-content",
        children=[
            dcc.Store(id="store-df", storage_type=storage),
            dcc.Store(id="df-classification", storage_type=storage),
            dcc.Store(id="df-area", storage_type=storage),
            dcc.Store(id="df-lat", storage_type=storage),
            dcc.Store(id="df-lon", storage_type=storage),
            dcc.Store(id="df-alt", storage_type=storage),
            dcc.Store(id="df-date", storage_type=storage),
            dcc.Store(id="df-env", storage_type=storage),
            dcc.Store(id="df-temp", storage_type=storage),
            dcc.Store(id="df-psd", storage_type=storage),
            dcc.Store(id="df-prop", storage_type=storage),
            dcc.Store(id="len-df", storage_type=storage),
            # dls.ThreeDots(
            #     [
            #     html.Div(
            #         className='row justify-content-around',
            #         children=[
            #             html.Div(
            #                 className='col-xs-12 col-sm-12 col-md-12 col-lg-12 col-xl-12',
            #                 children=[
            #                     dbc.Card(
            #                         [
            #                             dbc.CardHeader("Particle Location"),
            #                             dbc.CardBody(
            #                                 children=[
            #                                     dcc.Graph(
            #                                         id='top-down-map',
            #                                         figure={},
            #                                     ),
            #                                     html.P(
            #                                         'Hover over the image and choose the box select icon to update all figures based on selected location. \n \
            #                                         Select an empty region to reset view with all data points.',
            #                                         className='p text-center',
            #                                     ),
            #                                 ],
            #                             ),
            #                         ],
            #                         className='card-body',
            #                     )
            #                 ],
            #             ),
            #         ],
            #     ),
            # ],
            # ),
            dls.ThreeDots(
                [
                    dbc.Row(
                        [
                            html.Div(
                                children=[
                                    dbc.Card(
                                        children=[
                                            dbc.CardHeader("Particle Location"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="top-down-map",
                                                        figure={},
                                                    ),
                                                    html.P(
                                                        "Hover over the image"
                                                        " and choose the box"
                                                        " select icon to"
                                                        " update all figures"
                                                        " based on selected"
                                                        " location."
                                                        "Select an"
                                                        " empty region to"
                                                        " reset the view with all"
                                                        " data points. \n",
                                                        className=("p text-center"),
                                                    ),
                                                    html.P(
                                                        "Due to methodological constraints on the time resolution, multiple images are plotted at the same location. The number of overlaid images and majority classification (if applicable) are shown by hovering over a data point.",
                                                        className=("p text-center"),
                                                    ),
                                                ],
                                            ),
                                        ],
                                        className="card-body",
                                    ),
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                            html.Div(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                "Data points grouped into"
                                                " gridbox counts"
                                            ),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="density-contour",
                                                        figure={},
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                            html.Div(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Vertical Distribution"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="vert-dist",
                                                        figure={},
                                                    )
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                            html.Div(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Particle Type Percentage"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(id="pie", figure={})
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-6 col-md-6 col-lg-6" " col-xl-6"
                                ),
                            ),
                            # html.Div(
                            #     children=[
                            #         dbc.Card(
                            #             [
                            #                 dbc.CardHeader(
                            #                     "Normalized Particle Area"
                            #                     " Percentage by Count"
                            #                 ),
                            #                 dbc.CardBody(
                            #                     children=[
                            #                         dcc.Graph(
                            #                             id="pie-area",
                            #                             figure={},
                            #                         )
                            #                     ]
                            #                 ),
                            #             ],
                            #             className="card-body",
                            #         )
                            #     ],
                            #     className=(
                            #         "col-xs-12 col-sm-6 col-md-6 col-lg-3"
                            #         " col-xl-3"
                            #     ),
                            # ),
                        ],
                    ),
                ],
            ),
            dls.ThreeDots(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Geometric Property"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="prop-fig",
                                                        figure={},
                                                    )
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Environmental Property"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="type-env-violin",
                                                        figure={},
                                                    )
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                        ],
                    ),
                ]
            ),
            html.Hr(),
            dls.ThreeDots(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Particle Size Distribution"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id="psd-fig",
                                                        figure={},
                                                    )
                                                ]
                                            ),
                                        ],
                                        className="card-body",
                                    )
                                ],
                                className=(
                                    "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                                ),
                            ),
                            # dbc.Col(
                            #     children=[
                            #         dbc.Card(
                            #             [
                            #                 dbc.CardHeader("Mass-Dimensional Relationship"),
                            #                 dbc.CardBody(
                            #                     children=[
                            #                         dcc.Graph(
                            #                             id="md-fig",
                            #                             figure={},
                            #                         )
                            #                     ]
                            #                 ),
                            #             ],
                            #             className="card-body",
                            #         )
                            #     ],
                            #     className=(
                            #         "col-xs-12 col-sm-12 col-md-12 col-lg-6" " col-xl-6"
                            #     ),
                            # ),
                        ],
                    ),
                ]
            ),
            html.Hr(),
            html.P(
                "Copyright All Rights Reserved",
                id="copyright",
            ),
        ],
    )
    