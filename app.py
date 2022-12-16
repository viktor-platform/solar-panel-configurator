"""Copyright (c) 2022 VIKTOR B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

VIKTOR B.V. PROVIDES THIS SOFTWARE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from munch import Munch
from viktor.core import ViktorController, progress_message
from viktor.geometry import GeoPoint
from viktor.views import (
    DataGroup,
    DataItem,
    MapPoint,
    MapResult,
    MapView,
    PlotlyAndDataResult,
    PlotlyAndDataView,
    PlotlyResult,
    PlotlyView,
    WebResult,
    WebView,
)

from constants import inverter_name_dict, module_name_dict
from parametrization import ConfiguratorParametrization
from pv_calculations import calculate_energy_generation, get_location_data


class Controller(ViktorController):
    """Controller class which acts as interface for the Configurator entity type.
    Connects the Parametrization (left-side of web UI), with the Views (right-side of web UI)."""

    label = "Configurator"
    parametrization = ConfiguratorParametrization(width=30)
    viktor_enforce_field_constraints = True

    @MapView("Map", duration_guess=1)  # only visible on "Step 1"
    def get_map_view(self, params: Munch, **kwargs):
        """Creates mapview for step 1"""
        features = []

        if params.step_1.point:
            marker = params.step_1.point
            features.append(MapPoint.from_geo_point(marker))

        return MapResult(features)

    @PlotlyView(
        "Weather data",
        duration_guess=10,
        description="Based on location and historical weather data.",
    )
    def get_weather_data(self, params, **kwargs):
        """Visualizes the solar irradiance based on historical weather data."""
        location = params.step_1.point
        location_data = get_location_data(location.lat, location.lon)
        weather = location_data["weather"]
        x_dat = weather.index.strftime("%m-%d %H:%M").sort_values().tolist()
        temp_dat = weather["temp_air"].tolist()
        pressure_dat = weather["pressure"].tolist()
        wind_speed_dat = weather["wind_speed"].tolist()
        dni = weather["dni"].tolist()
        ghi = weather["ghi"].tolist()
        dhi = weather["dhi"].tolist()

        fig = {
            "data": [
                {
                    "type": "line",
                    "x": x_dat,
                    "y": dni,
                    "name": "Direct Normal Irradiance",
                    "visible": True,
                },
                {
                    "type": "line",
                    "x": x_dat,
                    "y": ghi,
                    "name": "Global Horizontal Irradiance",
                    "visible": True,
                },
                {
                    "type": "line",
                    "x": x_dat,
                    "y": dhi,
                    "name": "Diffuse Horizontal Irradiance",
                    "visible": True,
                },
                {
                    "type": "line",
                    "x": x_dat,
                    "y": temp_dat,
                    "name": "Air temperature",
                    "visible": False,
                },
                {
                    "type": "line",
                    "x": x_dat,
                    "y": pressure_dat,
                    "name": "Pressure",
                    "visible": False,
                },
                {
                    "type": "line",
                    "x": x_dat,
                    "y": wind_speed_dat,
                    "name": "Wind speed",
                    "visible": False,
                },
            ],
            "layout": {
                "title": {"text": "Weather data"},
                "xaxis": {"title": {"text": "Simulated year"}},
                "yaxis": {"title": {"text": ""}},
                "updatemenus": [
                    {
                        "buttons": [
                            {
                                "label": "Solar irradiance [W/m²]",
                                "method": "restyle",
                                "args": [
                                    "visible",
                                    [True, True, True, False, False, False],
                                ],
                            },
                            {
                                "label": "Air temperature [°C]",
                                "method": "restyle",
                                "args": [
                                    "visible",
                                    [False, False, False, True, False, False],
                                ],
                            },
                            {
                                "label": "Pressure [Pa]",
                                "method": "restyle",
                                "args": [
                                    "visible",
                                    [False, False, False, False, True, False],
                                ],
                            },
                            {
                                "label": "Wind speed [m/s]",
                                "method": "restyle",
                                "args": [
                                    "visible",
                                    [False, False, False, False, False, True],
                                ],
                            },
                        ]
                    }
                ],
            },
        }

        return PlotlyResult(fig)

    @PlotlyAndDataView("Data", duration_guess=10)  # only visible on "Step 2"
    def get_data_view(self, params: Munch, **kwargs):
        """Creates dataview for step 2 from the pv_calculation"""

        energy_yield_per_module, nr_modules, yield_df = self.get_energy_generation(
            location=params.step_1.point,
            inverter=params.step_2.inverter_name,
            solar_module=params.step_2.module_name,
            solar_surface_area=params.step_1.surface,
        )

        energy_info = DataItem(
            label="Yearly energy yield per module",
            value=energy_yield_per_module,
            suffix="Kwh/year",
            number_of_decimals=2,
        )
        number_of_modules = DataItem(
            label="Number of modules possible on surface",
            value=nr_modules,
            number_of_decimals=0,
        )
        inverter_cost = DataItem(
            label="Cost of Inverter",
            value=inverter_name_dict[params.step_2.inverter_name]["price"],
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )
        module_cost = DataItem(
            label="Cost per Module",
            value=module_name_dict[params.step_2.module_name]["price"],
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )
        total_cost = DataItem(
            label="Total system cost",
            value=inverter_name_dict[params.step_2.inverter_name]["price"]
            + module_name_dict[params.step_2.module_name]["price"] * nr_modules,
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )

        data = DataGroup(energy_info, number_of_modules, inverter_cost, module_cost, total_cost)

        # prepare data for plotly
        yield_df = yield_df.groupby(pd.Grouper(key="dat", freq="1D")).sum()
        yield_df["dat"] = yield_df.index.strftime("%Y-%m-%d %H:%M")
        x_dat = yield_df["dat"].to_list()
        y_dat = yield_df["val"].to_list()

        fig = {
            "data": [
                {"type": "bar", "x": x_dat, "y": y_dat, "name": "Energy yield"},
            ],
            "layout": {
                "title": {"text": "Electricity production simulated."},
                "xaxis": {"title": {"text": "Simulated year"}},
                "yaxis": {"title": {"text": "Yield [kWh/day]"}},
            },
        }

        return PlotlyAndDataResult(fig, data)

    @PlotlyView("Plot", duration_guess=10)  # only visible on "Step 3"
    def get_plotly_view(self, params: Munch, **kwargs):
        """Shows the plot of the energy yield with break-even point"""
        progress_message("Calculate energy generation...")
        _, nr_modules, yield_df = self.get_energy_generation(
            location=params.step_1.point,
            inverter=params.step_2.inverter_name,
            solar_module=params.step_2.module_name,
            solar_surface_area=params.step_1.surface,
        )

        progress_message("Extract yield data...")
        # get yearly yield data
        yield_df["val"] *= params.step_3.kwh_cost

        # calculate break-even (total costs / kwh price)
        break_even = (
            inverter_name_dict[params.step_2.inverter_name]["price"]
            + module_name_dict[params.step_2.module_name]["price"] * nr_modules
        )

        # forecast the length of the entered forecast horizon
        yield_df_copy = yield_df.copy()

        for i in range(1, params.step_3.forecast_horizon):
            new_year = yield_df_copy.copy()
            new_year["dat"] = self.replace_year(new_year["dat"], i)
            yield_df = yield_df.append(new_year)

        yield_df["dat"] = yield_df["dat"].dt.strftime("%Y-%m-%d %H:%M")

        # add a cumulative column
        yield_df["cumulative_yield"] = yield_df["val"].cumsum(axis=0)

        x_dat = yield_df["dat"].tolist()

        # prepare data for plotly
        y_dat = np.array(yield_df["cumulative_yield"])
        z_dat = np.full((len(x_dat)), break_even)

        idxs = np.argwhere(np.diff(np.sign(y_dat - z_dat))).flatten()
        _line = {}
        time_period = "-"
        if idxs:
            break_even_date = x_dat[idxs[0]]
            time_period = datetime.datetime.strptime(break_even_date, "%Y-%m-%d %H:%M") - datetime.datetime.strptime(
                x_dat[0], "%Y-%m-%d %H:%M"
            )
            time_period = round(time_period.days / 365, 1)
            _line = {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": break_even_date,
                "y0": 0,
                "x1": break_even_date,
                "y1": 1,
                "fillcolor": "#FF0000",
                "line": {
                    "width": 1,
                    "color": "#FF0000",
                },
            }

        progress_message("Plot results...")
        if params.step_3.break_even_toggle:
            fig = {
                "data": [
                    {
                        "type": "line",
                        "x": x_dat[::50],
                        "y": y_dat.tolist()[::50],
                        "name": "Energy yield",
                    },
                    {
                        "type": "line",
                        "x": x_dat[::50],
                        "y": z_dat.tolist()[::50],
                        "name": "Break-even point",
                    },
                ],
                "layout": {
                    "title": {"text": f"Energy generation over time (break-even = {time_period} years)"},
                    "xaxis": {"title": {"text": "Forecast horizon"}},
                    "yaxis": {"title": {"text": "Revenue produced by system [€]"}},
                },
            }
            if _line:
                fig["layout"]["shapes"] = [_line]
        else:
            fig = {
                "data": [
                    {
                        "type": "bar",
                        "x": x_dat[::50],
                        "y": y_dat.tolist()[::50],
                        "name": "Energy yield",
                    }
                ],
                "layout": {
                    "title": {"text": "Energy generation over time"},
                    "xaxis": {"title": {"text": "Forecast horizon"}},
                    "yaxis": {"title": {"text": "Revenue produced by system [€]"}},
                },
            }

        return PlotlyResult(fig)

    @staticmethod
    def get_energy_generation(location: GeoPoint, inverter: str, solar_module: str, solar_surface_area: float):
        """Generate energy yield data"""
        return calculate_energy_generation(
            latitude=location.lat,
            longitude=location.lon,
            inverter_name=inverter_name_dict[inverter]["name"],
            module_name=module_name_dict[solar_module]["name"],
            area=solar_surface_area,
        )

    @staticmethod
    def replace_year(frame, increment):
        """Update year of the dates in yield dataframe"""
        current_year = datetime.date.today().year
        frame = frame.apply(lambda dt: dt.replace(year=current_year + increment))
        return frame

    @WebView(" ", duration_guess=1)
    def final_step(self, params, **kwargs):
        """Initiates the process of rendering the last step."""
        html_path = Path(__file__).parent / "final_step.html"
        with html_path.open(encoding="utf-8") as _file:
            html_string = _file.read()
        return WebResult(html=html_string)
