# pylint:disable=line-too-long                                 # Allows for longer line length inside a Parametrization
"""Copyright (c) 2022 VIKTOR B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

VIKTOR B.V. PROVIDES THIS SOFTWARE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from viktor.parametrization import (
    Parametrization,
    Step,
    NumberField,
    GeoPointField,
    Tab,
    OptionField,
    ToggleButton
)
from munch import Munch

def _get_inverter_name_list(params: Munch, **kwargs):
    """Create list of options for the inverter name dependent on the type"""
    if params.step_2.system_type == "California Energy Commission":
        return [
            "ABB: MICRO-0.3 Inverter",
            "Outback Power Tech. Inverter",
            "Hanwa Q-Cells Inverter", ##########
        ]
    if params.step_2.system_type == "Sandia National Laboratories":
        return [
            "Generac Power Systems Inverter",
            "Delta Electronics Inverter",
            "Chint Power Systems Inverter", #############
        ]
    return []


class ConfiguratorParametrization(Parametrization):
    """Defines the input fields for the mapview (step 1) and dataview (step 2)"""

    step_1 = Step("Step 1 Home", views="get_map_view")  # no views
    step_1.location = Tab("Location")
    step_1.location.point = GeoPointField("enter a point")
    step_1.location.surface = NumberField("Surface area", suffix="m2", default=0)

    step_2 = Step("Step 2 System", views="get_data_view")
    # add comment which explains that Sandia and CEC are
    # two approval protocols for calculating the inverter's output power
    # Sandia explanation: (https://energy.sandia.gov/wp-content/gallery/uploads/
    #                                               Performance-Model-for-Grid-Connected-Photovoltaic-Inverters.pdf)
    # CEC explanation: (https://www.energy.ca.gov/sites/default/files/2020-06/2004-11-22_Sandia_Test_Protocol_ada.pdf)
    step_2.system_type = OptionField(
        "System type",
        options=["Sandia National Laboratories", "California Energy Commission"],
        default="Sandia National Laboratories", flex=70,
        autoselect_single_option=True
    )

    step_2.inverter_name = OptionField(
        "Inverter model", options=_get_inverter_name_list, default="Generac Power Systems Inverter",
        flex=50, autoselect_single_option=True,

    )

    step_2.module_name = OptionField(
        "Module model",
        options=[
            "AstroPower APX-120",
            "BP Solar SX160B",
            "Kyocera Solar PV110",
            "Mitsubishi PV - MF185UD4",
            "Sanyo HIP - 200BE11",
            "Sharp ND - L3E1U",
            "Siemens Solar SP75(6V)",
            "Suntech STP200S - 18 - ub - 1 Module",
        ],
        flex=50, autoselect_single_option=True, default='AstroPower APX-120'
    )

    # Step 3 contains the calculation of the break-even point and visualisation thereof
    step_3 = Step('Step 3 Visualisation', views='get_plotly_view')
    step_3.forecast_horizon = NumberField('Enter the forecasting horizon', suffix='years', default=5, flex=80)
    step_3.kwh_cost = NumberField('Enter KWh price to calculate break-even', suffix='€/KWh', default=0.22, flex=80)
    step_3.break_even_toggle = ToggleButton('Show break-even point', default=True)

