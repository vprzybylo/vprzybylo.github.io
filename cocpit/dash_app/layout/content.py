'''Set up the app layout'''

import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
import globals
from dash import dcc, html


def header_cards(
    class_name_header,
    class_name_body,
    title,
    id_header,
    id_body,
    campaign='CRYSTAL FACE (UND)',
):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className=class_name_header, id=id_header),
                    html.P(
                        globals.campaign_image_count[campaign],
                        className=class_name_body,
                        id=id_body,
                    ),
                ]
            )
        ],
        className='top-cards',
    )


def content():

    storage = 'session'
    return html.Div(
        id="page-content",
        children=[
            dcc.Store(id='store-df', storage_type=storage),
            dcc.Store(id='df-classification', storage_type=storage),
            dcc.Store(id='df-lat', storage_type=storage),
            dcc.Store(id='df-lon', storage_type=storage),
            dcc.Store(id='df-alt', storage_type=storage),
            dcc.Store(id='df-env', storage_type=storage),
            dcc.Store(id='df-temp', storage_type=storage),
            dcc.Store(id='df-prop', storage_type=storage),
            dcc.Store(id='len-df', storage_type=storage),
            dls.Hash(
                dbc.Row(
                    dbc.Col(
                        header_cards(
                            'card-title',
                            'card-text',
                            'Number of images',
                            'card-header-images',
                            'card-text-images',
                        ),
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=6,
                    ),
                    align="center",
                    justify="center",
                ),
            ),
            dbc.Row(
                [
                    # dbc.Col(
                    #     [
                    #         dbc.Row(
                    #             dbc.Label('Vertical Axis Property:'),
                    #         ),
                    #         dbc.Row(
                    #             dcc.Dropdown(
                    #                 id='3d_vertical_prop',
                    #                 options=[
                    #                     {'label': i, 'value': i}
                    #                     for i in globals.vertical_vars
                    #                 ],
                    #                 placeholder="Vertical Axis Property",
                    #                 value='Temperature',
                    #             ),
                    #         ),
                    #     ],
                    #     xs=12,
                    #     sm=12,
                    #     md=12,
                    #     lg=12,
                    #     xl=2,
                    # ),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                [
                                    dbc.CardHeader("Particle Location"),
                                    dbc.CardBody(
                                        children=[
                                            dcc.Graph(
                                                id='top-down-map',
                                                figure={},
                                            ),
                                            html.P(
                                                'Hover over image and choose box select icon to update all figures based on chosen location. \n \
                                                Select empty region to reset view with all data points.',
                                                style={
                                                    'text-align': 'center',
                                                    'margin': '0px',
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                className='card-body',
                            )
                        ],
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=6,
                    ),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                [
                                    dbc.CardHeader("Particle Type Percentage"),
                                    dbc.CardBody(
                                        children=[dcc.Graph(id='pie', figure={})]
                                    ),
                                ],
                                className='card-body',
                            )
                        ],
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=6,
                    ),
                ],
                align="center",
                justify="center",
            ),
            dls.Hash(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Cross-Section (Longitude)"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id='lon-alt-hist', figure={}
                                                    )
                                                ]
                                            ),
                                        ],
                                        className='card-body',
                                    )
                                ],
                                xs=12,
                                sm=12,
                                md=12,
                                lg=12,
                                xl=6,
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Cross Section (Latitude)"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id='lat-alt-hist', figure={}
                                                    )
                                                ]
                                            ),
                                        ],
                                        className='card-body',
                                    )
                                ],
                                xs=12,
                                sm=12,
                                md=12,
                                lg=12,
                                xl=6,
                            ),
                        ],
                        align="center",
                        justify="center",
                    ),
                ],
            ),
            dls.Hash(
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
                                                    dcc.Graph(id='prop-fig', figure={})
                                                ]
                                            ),
                                        ],
                                    )
                                ],
                                xs=12,
                                sm=12,
                                md=12,
                                lg=12,
                                xl=6,
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Environmental Attributes"),
                                            dbc.CardBody(
                                                children=[
                                                    dcc.Graph(
                                                        id='type-env-violin', figure={}
                                                    )
                                                ]
                                            ),
                                        ],
                                    )
                                ],
                                xs=12,
                                sm=12,
                                md=12,
                                lg=12,
                                xl=6,
                            ),
                        ],
                        align="center",
                        justify="center",
                    ),
                ]
            ),
            html.P(
                'Copyright All Rights Reserved',
                id='copyright',
            ),
        ],
    )
