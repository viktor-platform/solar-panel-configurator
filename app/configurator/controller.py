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

from munch import Munch
from .parametrization import ConfiguratorParametrization
from .pv_calculations import calculate_energy_generation


class Controller(ViktorController):
    """Controller class which acts as interface for the Configurator entity type.
    Connects the Parametrization (left-side of web UI), with the Views (right-side of web UI)."""

    label = "Configurator"
    parametrization = ConfiguratorParametrization(width=20)
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
        type_dict = {'CEC Module': 'cecmod',
                     'Sandia Module': 'sandiamod',
                     'CEC Inverter': 'cecinverter',
                     'Sandia Inverter': 'sandiainverter'
                     }
        module_name_dict = {'First the CEC modules' : 'here',
                     'Jinko Solar JKM260P-60 Module': 'Jinko Solar Co._ Ltd JKM260P-60',
                     'Canadian Solar CS6K-270P Module': 'Canadian Solar Inc. CS6K-270P',
                     'Canadian Solar CS6K-275M Module': 'Canadian Solar Inc. CS6K-275M',
                     'Hanwha Q CELLS Q.PLUS BFR-G4.1 280 Module': 'Hanwha Q CELLS Q.PLUS BFR G4.1 280',
                     'Hanwha Q CELLS Q.Peak-G4.1 300 Module': 'Hanwha Q CELLS Q.PEAK-G4.1 300',
                     'Panasonic VBHN325SA 16 Module': 'SANYO ELECTRIC CO LTD OF PANASONIC GROUP VBHN325SA16',
                     'LG LG320N1K-A5 Module': 'LG Electronics Inc. LG320N1K-A5',
                     'Mission Solar MSE300SQ5T Module': 'Mission Solar Energy MSE300SQ5T',
                     'itek Energy IT-360-SE72 Module': 'Itek Energy LLC iT-360-SE-72',
                     'Then the Sandia modules': 'here',
                     'AstroPower APX-120': 'AstroPower APX-120 [ 2001]',
                     'BP Solar SX160B': 'BP Solar SX160B [2005 (E)]',
                     'Kyocera Solar PV110': 'Kyocera Solar PV110 [2003 (E)]',
                     'Mitsubishi PV - MF185UD4': 'Mitsubishi PV-MF185UD4 [2006 (E)]',
                     'Sanyo HIP - 200BE11': 'Sanyo HIP-200BE11 [2006 (E)]',
                     'Sharp ND - L3E1U': 'Sharp ND-L3E1U [2002 (E)]',
                     'Siemens Solar SP75(6V)': 'Siemens Solar SP75 (6V) [2003 (E)]',
                     'Suntech STP200S - 18 - ub - 1 Module': 'Suntech STP200S-18-ub-1 Module [2009 (E)]'}

        inverter_name_dict = {'First the CEC modules': 'here',
                            'ABB: MICRO-0.3 Inverter': 'ABB: MICRO-0.3-I-OUTD-US-240 [240V]',
                            'Outback Power Tech. Inverter': ' OutBack Power Technologies - Inc : GS8048A [240V]',
                            'Hanwa Q-Cells Inverter': 'Hanwha Q CELLS America Inc : Q.HOME+ HYB-G1-7.6 [240V]',
                            'Then the Sandia modules': 'here',
                            'Generac Power Systems Inverter': ' Generac Power Systems: XVT076A03 [240V]',
                            'Delta Electronics Inverter': ' Delta Electronics: E4-TL-US(AC) [240V]',
                            'Chint Power Systems Inverter': ' Chint Power Systems America: CPS ECB30KTL-O/US [480V]'
                            }

        energy_generation = calculate_energy_generation(
            params.step_1.location.point.lat,
            params.step_1.location.point.lon,
            type_dict[params.step_2.inverter_type],
            type_dict[params.step_2.module_type],
            module_name_dict[params.step_2.module_name],
            inverter_name_dict[params.step_2.inverter_name],
            area=params.step_1.location.surface
        )

        data = DataGroup(
            DataItem(
                label="Yearly energy yield", value=energy_generation, suffix="Kwh/year", number_of_decimals=3
            )
        )

        return DataResult(data)
