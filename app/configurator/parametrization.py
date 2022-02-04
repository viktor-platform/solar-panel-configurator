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
from viktor.parametrization import Parametrization, Step, NumberField, BooleanField, GeoPointField, Tab, Section
from viktor.parametrization import OptionField


class ConfiguratorParametrization(Parametrization):
    step_1 = Step('Step 1 Home', views='get_map_view')  # no views
    step_1.location = Tab("Location")
    step_1.location.point = GeoPointField("enter a point")

    step_1.location.surface = NumberField('Surface area', suffix='m2', default=0)


    step_2 = Step('Step 2 Panels', views='get_data_view')
    step_2.panels = Tab('Panels')
    step_2.panels.type = OptionField('Panel type', options=['type1', 'type2'], default='type1')