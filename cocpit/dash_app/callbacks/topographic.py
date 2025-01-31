"""
plot topographic map
scatter plot overlaid where particle images were captured
includes callbacks
"""
import plotly.graph_objects as go
import os
import pandas as pd
import plotly.express as px
from processing_scripts import process
from dash_extensions.enrich import Input, Output
import globals
import numpy as np


def register(app):
    @app.callback(
        Output("density-contour", "figure"),
        [
            Input("df-classification", "data"),
            Input("df-lat", "data"),
            Input("df-lon", "data"),
        ],
    )
    def density_contour(df_classification, df_lat, df_lon):
        """2D histogram of particles (top down view)"""

        # group individual points into grids
        gridx = np.linspace(df_lon.min(), df_lon.max())
        gridy = np.linspace(df_lat.min(), df_lat.max())
        # count number of points per grid based on lat and lon
        grid, _, _ = np.histogram2d(df_lon, df_lat, bins=[gridx, gridy])

        # find center points of every gridbox for plotting heatmap
        centers_x = [(a + b) / 2 for a, b in zip(gridx, gridx[1:])]
        centers_y = [(a + b) / 2 for a, b in zip(gridy, gridy[1:])]

        # Plotting each grids (x,y) center point.
        # For each one of those points, the color will
        # correspond to the # of points per grid box.
        # grid is 2D whereas centers_x (longitudes) and
        # centers_y (latitudes) are 1D so repeat lats and lons
        # so that all arrays are the same length
        center_xs = []
        center_ys = []
        counts = []
        for x, center_x in enumerate(centers_x):
            for y, center_y in enumerate(centers_y):
                counts.append(grid[x, y])
                center_xs.append(center_x)
                center_ys.append(center_y)

        fig = px.density_mapbox(
            lat=center_ys,
            lon=center_xs,
            z=counts,
            color_continuous_scale=px.colors.sequential.OrRd_r,
            radius=10,
            center=dict(lat=df_lat.mean(), lon=df_lon.mean()),
            zoom=5,
            mapbox_style="stamen-terrain",
        )
        fig.layout.coloraxis.colorbar.title = "Number <br>of Images"
        fig.update_traces(hovertemplate="# per gridbox: %{z}")

        return process.update_layout(fig, contour=True, margin=5)

    @app.callback(
        Output("top-down-map", "figure"),
        [
            Input("df-classification", "data"),
            Input("df-lat", "data"),
            Input("df-lon", "data"),
        ],
    )
    def map_top_down(df_classification, df_lat, df_lon):
        """aircraft location and particle type overlaid on map"""
        
        df_concat = pd.concat([df_classification, df_lat, df_lon], axis=1)
        
        
        grouped_count = df_concat.groupby(["Latitude [degrees]", "Longitude [degrees]"], as_index=False)['Classification'].agg('count')

        grouped_mode = df_concat.groupby(["Latitude [degrees]", "Longitude [degrees]"], as_index=False)['Classification'].agg(pd.Series.mode)
        
        mode_list = grouped_mode['Classification'].values.tolist()
        mask_multimode = []
        for element in mode_list:
            if isinstance(element, np.ndarray):
                mask_multimode.append('Multiple Modes')
            else:
                mask_multimode.append(element)

        grouped_mode['Classification'] = mask_multimode

        fig = px.scatter_mapbox(
            lat=grouped_count["Latitude [degrees]"],
            lon=grouped_count["Longitude [degrees]"],
            size=grouped_count['Classification'],
            color=grouped_mode['Classification'],
            color_discrete_map=globals.color_discrete_map,
            mapbox_style="stamen-terrain",
            custom_data=[grouped_count["Latitude [degrees]"],
                grouped_count["Longitude [degrees]"],
                grouped_count['Classification'],
                grouped_mode['Classification'],
            ]
        )

        fig.update_traces(
            hovertemplate='Latitude: %{customdata[0]:.2f}<br>'+
                        'Longitude %{customdata[1]:.2f}<br>'+
                        'Image count: %{customdata[2]}<br>'+
                        'Majority classification: %{customdata[3]}<br>')

        # Specify layout information
        fig.update_layout(
            mapbox=dict(
                accesstoken=os.getenv("MAPBOX_TOKEN"),
                center=dict(lon=df_lon.mean(), lat=df_lat.mean()),
                zoom=5,
            ),
        )
        return process.update_layout(fig, contour=True, margin=5)

    @app.callback(
        Output("vert-dist", "figure"),
        Input("df-alt", "data"),
        Input("df-classification", "data"),
    )
    def vert_distribution(df_alt, df_classification):

        # df_alt = df_alt.replace([-999.99, -999.0, np.inf, -np.inf], np.nan)
        # df_classification = df_classification[df_alt != np.nan]
        # df_lon = df_lon[df_alt != np.nan]
        # df_alt = df_alt.dropna()

        vert_dist = px.violin(
            x=df_classification,
            y=df_alt,
            color=df_classification,
            color_discrete_map=globals.color_discrete_map,
            labels={
                "x": "Particle Type",
                "y": "Altitude [m]",
            },
        )

        vert_dist = process.update_layout(vert_dist, contour=False)
        return vert_dist
