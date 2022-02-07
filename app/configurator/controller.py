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
from viktor.views import DataResult, DataView, DataItem, DataGroup
from viktor.views import MapPoint, MapResult, MapView

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
        e_yield = calculate_energy_generation(
            params.step_1.location.point.lat, params.step_1.location.point.lon
        )

        data = DataGroup(
            DataItem(label="Yearly energy yield", value=e_yield, suffix="Kwh/year")
        )

        return DataResult(data)
