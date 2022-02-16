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
import datetime
import pvlib
import pandas as pd


def calculate_energy_generation(
    latitude,
    longitude,
    inverter_type,
    inverter_name,
    module_name,
    area=2,
    module_type="sandiamod",
):
    """Calculates the yearly energy yield as a result of the coorinates"""

    def translate_names(entry):
        """Translates module and inverter names to suit with the SAM databases"""
        bad_chars = ' -.()[]:+/",'
        good_chars = "____________"
        trans_dict = entry.maketrans(bad_chars, good_chars)
        translated_entry = entry.translate(trans_dict)

        return translated_entry

    # get the module and inverter databases from SAM
    url_dict = {
        "cecmod": "https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/CEC%20Modules.csv",
        "sandiamod": "https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/Sandia%20Modules.csv",
        "cecinverter": "https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/CEC%20Inverters.csv",
        "sandiainverter": "https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/CEC%20Inverters.csv",
    }
    # get module and inverter information from the databases
    modules_types = pvlib.pvsystem.retrieve_sam(None, url_dict[module_type])
    inverters_types = pvlib.pvsystem.retrieve_sam(None, url_dict[inverter_type])
    module = modules_types[translate_names(module_name)]
    inverter = inverters_types[translate_names(inverter_name)]

    # get module area information and calculate the amount of modules possible
    if module_type == "cecmod":
        surface_area = module["A_c"]
    elif module_type == "sandiamod":
        surface_area = module["Area"]
    else:
        raise ValueError("Incorrect value for module type")

    nr_modules = area // surface_area

    # get temperature specifications of module materials (default most used in consumer-systems)
    temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
        "sapm"
    ]["open_rack_glass_glass"]

    # retreive weather data and elevation (altitude)
    weather, *inputs = pvlib.iotools.get_pvgis_tmy(
        latitude, longitude, map_variables=True
    )
    weather.index.name = "utc_time"
    temp_air = weather["temp_air"]  # [degrees_C]
    wind_speed = weather["wind_speed"]  # [m/s]
    pressure = weather["pressure"]  # [Pa]
    altitude = inputs[1]["location"]["elevation"]  # [m]

    # declare system
    system = {"module": module, "inverter": inverter, "surface_azimuth": 180}
    system["surface_tilt"] = latitude

    # determine solar position
    solpos = pvlib.solarposition.get_solarposition(
        time=weather.index,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        temperature=temp_air,
        pressure=pressure,
    )

    # calculate energy produced based on entered data
    dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos["apparent_zenith"])
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    aoi = pvlib.irradiance.aoi(
        system["surface_tilt"],
        system["surface_azimuth"],
        solpos["apparent_zenith"],
        solpos["azimuth"],
    )
    total_irrad = pvlib.irradiance.get_total_irradiance(
        system["surface_tilt"],
        system["surface_azimuth"],
        solpos["apparent_zenith"],
        solpos["azimuth"],
        weather["dni"],
        weather["ghi"],
        weather["dhi"],
        dni_extra=dni_extra,
        model="haydavies",
    )

    tcell = pvlib.temperature.sapm_cell(
        total_irrad["poa_global"], temp_air, wind_speed, **temperature_model_parameters
    )

    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
        total_irrad["poa_direct"], total_irrad["poa_diffuse"], am_abs, aoi, module
    )
    dc_yield = pvlib.pvsystem.sapm(effective_irradiance, tcell, module)
    ac_yield = pvlib.inverter.sandia(
        dc_yield["v_mp"] * nr_modules, dc_yield["p_mp"] * nr_modules, inverter
    )
    ac_yield_per_module = pvlib.inverter.sandia(
        dc_yield["v_mp"], dc_yield["p_mp"], inverter
    )

    # output for the energy per module
    yield_per_module = ac_yield_per_module.to_frame()
    yield_per_module["utc_time"] = pd.to_datetime(yield_per_module.index)
    yield_per_module.columns = ["val", "dat"]
    yield_per_module.val *= 0.001

    # prepare data for presentation and visualisation
    acdf = ac_yield.to_frame()
    acdf["utc_time"] = pd.to_datetime(acdf.index)
    acdf["utc_time"] = acdf["utc_time"].apply(
        lambda dt: dt.replace(year=datetime.date.today().year)
    )

    acdf.columns = ["val", "dat"]

    acdf.val *= 0.001
    acdf.fillna(0, inplace=True)

    # possible plot
    acdf.plot(x="dat", y="val")
    annual_energy = yield_per_module["val"].sum()
    # plt.show()

    # final result in KWh*hrs
    energy_yield_per_module = int(annual_energy)

    return energy_yield_per_module, nr_modules, acdf
