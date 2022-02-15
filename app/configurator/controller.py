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
from viktor.core import ViktorController
from viktor.views import DataResult
from viktor.views import DataView
from viktor.views import DataItem
from viktor.views import DataGroup
from viktor.views import MapPoint
from viktor.views import MapResult
from viktor.views import MapView
from viktor.views import PlotlyView
from viktor.views import PlotlyResult

from munch import Munch
from .parametrization import ConfiguratorParametrization
from .pv_calculations import calculate_energy_generation


class Controller(ViktorController):
    """Controller class which acts as interface for the Configurator entity type.
    Connects the Parametrization (left-side of web UI), with the Views (right-side of web UI)."""

    label = "Configurator"
    parametrization = ConfiguratorParametrization(width=30)
    viktor_convert_entity_field = True

    @MapView("Map", duration_guess=1)  # only visible on "Step 1"
    def get_map_view(self, params: Munch, **kwargs):
        """Creates mapview for step 1"""
        features = []

        if params.step_1.location.point:
            marker = params.step_1.location.point
            features.append(MapPoint.from_geo_point(marker))

        return MapResult(features)

    @DataView("Data", duration_guess=1)  # only visible on "Step 2"
    def get_data_view(self, params, **kwargs):
        """Creates dataview for step 2 from the pv_calculation"""
        type_dict = {
            "California Energy Commission": "cecinverter",
            "Sandia National Laboratories": "sandiainverter",
        }
        module_name_dict = {
            "AstroPower APX-120": {
                "name": "AstroPower APX-120 [ 2001]",
                "price": 132.32,
            },
            "BP Solar SX160B": {"name": "BP Solar SX160B [2005 (E)]", "price": 132.32},
            "Kyocera Solar PV110": {
                "name": "Kyocera Solar PV110 [2003 (E)]",
                "price": 132.32,
            },
            "Mitsubishi PV - MF185UD4": {
                "name": "Mitsubishi PV-MF185UD4 [2006 (E)]",
                "price": 154.20,
            },
            "Sanyo HIP - 200BE11": {
                "name": "Sanyo HIP-200BE11 [2006 (E)]",
                "price": 132.32,
            },
            "Sharp ND - L3E1U": {"name": "Sharp ND-L3E1U [2002 (E)]", "price": 675.00},
            "Siemens Solar SP75(6V)": {
                "name": "Siemens Solar SP75 (6V) [2003 (E)]",
                "price": 50.00,
            },
            "Suntech STP200S - 18 - ub - 1 Module": {
                "name": "Suntech STP200S-18-ub-1 Module [2009 (E)]",
                "price": 480.00,
            },
        }

        inverter_name_dict = {
            "ABB: MICRO-0.3 Inverter": {                        # First three CEC Inverters
                "name": "ABB: MICRO-0.3-I-OUTD-US-240 [240V]",
                "price": 173.19,
            },
            "Outback Power Tech. Inverter": {
                "name": " OutBack Power Technologies - Inc : GS8048A [240V]",
                "price": 3791.88,
            },
            "Hanwa Q-Cells Inverter": {
                "name": "Hanwha Q CELLS America Inc : Q.HOME+ HYB-G1-7.6 [240V]",
                "price": 999.99,
            },
            "Generac Power Systems Inverter": {                 # Second three Sandia Inverters
                "name": " Generac Power Systems: XVT076A03 [240V]",
                "price": 3431.35,
            },
            "Delta Electronics Inverter": {
                "name": " Delta Electronics: E4-TL-US(AC) [240V]",
                "price": 999.99,
            },
            "Chint Power Systems Inverter": {
                "name": " Chint Power Systems America: CPS ECB30KTL-O/US [480V]",
                "price": 999.99,
            },
        }

        energy_generation = calculate_energy_generation(
            params.step_1.location.point.lat,
            params.step_1.location.point.lon,
            type_dict[params.step_2.system_type],
            inverter_name_dict[params.step_2.inverter_name]["name"],
            module_name_dict[params.step_2.module_name]["name"],
            area=params.step_1.location.surface,
        )

        energy_info = DataItem(
            label="Yearly energy yield",
            value=energy_generation[0],
            suffix="Kwh/year",
            number_of_decimals=3,
        )
        inverter_cost = DataItem(
            label="Inverter cost",
            value=inverter_name_dict[params.step_2.inverter_name]["price"],
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )
        module_cost = DataItem(
            label="Module costs",
            value=module_name_dict[params.step_2.module_name]["price"],
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )
        total_cost = DataItem(
            label="Total system cost",
            value=inverter_name_dict[params.step_2.inverter_name]["price"]
            + module_name_dict[params.step_2.module_name]["price"]
            * energy_generation[1],
            prefix="€",
            suffix=",-",
            number_of_decimals=2,
        )

        data = DataGroup(energy_info, inverter_cost, module_cost, total_cost)

        return DataResult(data)

    @PlotlyView('Plot', duration_guess=1) #only visible on "Step 3"
    def get_plotly_view(self, params, **kwargs):
        """Shows the plot of the energy yield with break-even point"""

        # re-do the energy calculation:
        type_dict = {
            "California Energy Commission": "cecinverter",
            "Sandia National Laboratories": "sandiainverter",
        }
        module_name_dict = {
            "AstroPower APX-120": {
                "name": "AstroPower APX-120 [ 2001]",
                "price": 132.32,
            },
            "BP Solar SX160B": {"name": "BP Solar SX160B [2005 (E)]", "price": 132.32},
            "Kyocera Solar PV110": {
                "name": "Kyocera Solar PV110 [2003 (E)]",
                "price": 132.32,
            },
            "Mitsubishi PV - MF185UD4": {
                "name": "Mitsubishi PV-MF185UD4 [2006 (E)]",
                "price": 154.20,
            },
            "Sanyo HIP - 200BE11": {
                "name": "Sanyo HIP-200BE11 [2006 (E)]",
                "price": 132.32,
            },
            "Sharp ND - L3E1U": {"name": "Sharp ND-L3E1U [2002 (E)]", "price": 675.00},
            "Siemens Solar SP75(6V)": {
                "name": "Siemens Solar SP75 (6V) [2003 (E)]",
                "price": 50.00,
            },
            "Suntech STP200S - 18 - ub - 1 Module": {
                "name": "Suntech STP200S-18-ub-1 Module [2009 (E)]",
                "price": 480.00,
            },
        }
        inverter_name_dict = {
            "ABB: MICRO-0.3 Inverter": {  # First three CEC Inverters
                "name": "ABB: MICRO-0.3-I-OUTD-US-240 [240V]",
                "price": 173.19,
            },
            "Outback Power Tech. Inverter": {
                "name": " OutBack Power Technologies - Inc : GS8048A [240V]",
                "price": 3791.88,
            },
            "Hanwa Q-Cells Inverter": {
                "name": "Hanwha Q CELLS America Inc : Q.HOME+ HYB-G1-7.6 [240V]",
                "price": 999.99,
            },
            "Generac Power Systems Inverter": {  # Second three Sandia Inverters
                "name": " Generac Power Systems: XVT076A03 [240V]",
                "price": 3431.35,
            },
            "Delta Electronics Inverter": {
                "name": " Delta Electronics: E4-TL-US(AC) [240V]",
                "price": 999.99,
            },
            "Chint Power Systems Inverter": {
                "name": " Chint Power Systems America: CPS ECB30KTL-O/US [480V]",
                "price": 999.99,
            },
        }

        energy_generation = calculate_energy_generation(
            params.step_1.location.point.lat,
            params.step_1.location.point.lon,
            type_dict[params.step_2.system_type],
            inverter_name_dict[params.step_2.inverter_name]["name"],
            module_name_dict[params.step_2.module_name]["name"],
            area=params.step_1.location.surface,
        )

        yield_df = energy_generation[2]
        break_even = (inverter_name_dict[params.step_2.inverter_name]["price"] +
                      module_name_dict[params.step_2.module_name]["price"] *
                      energy_generation[1]) / params.step_3.kwh_cost

        x_dat = yield_df['dat'].to_list()
        y_dat = yield_df['cumulative_yield'].to_list()
        z_dat = [break_even] * len(x_dat)

        fig = {
            "data": [{"type": "bar", "x": x_dat, "y": y_dat}, {"type": "line", "x": x_dat, "y": z_dat}],
            "layout": {"title": {"text": "Energy generation over time"}}
        }

        return PlotlyResult(fig)
