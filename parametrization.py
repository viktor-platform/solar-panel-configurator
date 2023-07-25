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
from munch import Munch
from viktor.errors import UserError
from viktor.geometry import GeoPoint
from viktor.parametrization import (
    GeoPointField,
    NumberField,
    OptionField,
    Parametrization,
    Step,
    Text,
    ToggleButton,
)

from constants import inverter_name_dict

DEFAULT_LOCATION = GeoPoint(51.92230888213379, 4.469658812222693)


def validate_step_1(params, **kwargs):
    """Validates step 1."""
    if not params.step_1.point:
        raise UserError("Select a location on the map.")
    if params.step_1.surface == 0:
        raise UserError("The surface area should be larger than zero.")


def _get_inverter_name_list(params: Munch, **kwargs):
    """Create list of options for the inverter name dependent on the type"""
    inverter_names = list(inverter_name_dict.keys())
    if params.step_2.system_type == "California Energy Commission":
        return inverter_names[3:]
    if params.step_2.system_type == "Sandia National Laboratories":
        return inverter_names[:3]
    return []


class ConfiguratorParametrization(Parametrization):
    """Defines the input fields for the mapview (step 1) and dataview (step 2)"""

    step_1 = Step(
        "Step 1 Define location of your home",
        views=["get_map_view", "get_weather_data"],
        on_next=validate_step_1,
    )

    step_1.text = Text(
        """# Welcome to the Solar configurator app!
This app allows one to design and calculate the return-on-investment for a PV system in a simplified manner.

## Location definition

Different locations around the globe interact with the sun differently.

Moreover the different climates produce specific weather patterns.

By choosing the location of your home on the map on the right, weather data for a
*Typical Meteorological Year* (TMY) at your location will be gathered from the
[EU Science Hub](https://ec.europa.eu/jrc/en/pvgis). This TMY is used in the calculation of energy yield by your
system.

## Choose location
"""
    )
    step_1.point = GeoPointField(
        "enter a point",
        description="Click a location on the map to select it for calculation",
        default=DEFAULT_LOCATION,
    )
    step_1.text3 = Text("""Define the surface area available on the roof:""")
    step_1.surface = NumberField(
        "Surface area",
        suffix="m2",
        default=20,
        min=10,
        max=200,
        description="Use the arrows to select your available surface area or enter a number "
        "  \n (if applicable use a decimal point **' . '** instead of a comma **' , '** )",
    )

    step_2 = Step("Step 2 Choose your system configuration", views="get_data_view")

    step_2.text = Text(
        """## PV-System explanation
A consumer-home PV-system always consist of
- One inverter unit
- One or more modules
The PV-systems included here are all approved by either the
[Sandia National Laboratory](https://tinyurl.com/4jf5nkpy) or the
[California Energy Commission](https://tinyurl.com/2p87uwkj), both of which use different calculations
for their approval protocols.
"""
    )
    step_2.text2 = Text(
        """## Choose PV-System configuration
By choosing either institution as the *System type* one is able to choose different 
configurations of inverters and modules.

All up-to-date secifications of the chosen system configuration are
provided by the *System Advisor Model* (SAM) as developed by the
[National Renewable Energy Laboratory](https://sam.nrel.gov/).
"""
    )

    step_2.system_type = OptionField(
        "System type",
        options=["Sandia National Laboratories", "California Energy Commission"],
        default="Sandia National Laboratories",
        flex=70,
        autoselect_single_option=True,
    )

    step_2.inverter_name = OptionField(
        "Inverter model",
        options=_get_inverter_name_list,
        default="ABB: PVI-0.3 Inverter",
        flex=50,
        autoselect_single_option=True,
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
        flex=50,
        autoselect_single_option=True,
        default="AstroPower APX-120",
    )

    # Step 3 contains the calculation of the break-even point and visualisation thereof
    step_3 = Step("Step 3 Visualise your return-on-investment", views="get_plotly_view")
    step_3.text = Text(
        """## Forecast and Break-even
Here you are able to forecast the energy yield of your chosen system. Based on the **kWh price** indicated
The forecast will automatically calculate the revenue produced by your system.

The break-even point is also indicated, this is the moment in time where the investment will be fully
compensated by the revenue produced.
"""
    )
    step_3.forecast_horizon = NumberField(
        "Enter the forecasting horizon",
        suffix="years",
        default=5,
        flex=80,
        min=1,
        description="Amount of years starting at" "  \n the beginning of this year" "  \n (enter only whole years)",
    )
    step_3.kwh_cost = NumberField(
        "Enter kWh price to calculate break-even",
        suffix="€/kWh",
        default=0.65,
        flex=80,
        min=0,
        step=0.1,
        description="kWh price which is applicable to you."
        "  \n Prices may differ between energy providers."
        " \n"
        "  \n Note that prices for kWh supplied **to** the grid often"
        " differ from those of kWhs **taken from** the grid",
    )
    step_3.text2 = Text(
        """If you are only interested in a detailed time period you could choose to not show the break-even point
in the graph and choose for a short forecasting horizon.

Alternatively you could use the viewing-tools in the top-right corner of the graph to zoom to a specific
point.
"""
    )
    step_3.break_even_toggle = ToggleButton("Show break-even point", default=True)

    final_step = Step("What's next?", views="final_step")
