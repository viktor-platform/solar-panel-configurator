import pandas as pd
import matplotlib.pyplot as plt
import pvlib
from timezonefinder import TimezoneFinder


def calculate_energy_generation(Lat, Lon):
    latitude = Lat
    longitude = Lon
    name = "Your"

    # determine the altitude based on coordinates
    altitude = 0

    # determine the timezone based on coordinates
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lng=longitude, lat=latitude)

    # get the module and inverter specifications from SAM
    sandia_modules = pvlib.pvsystem.retrieve_sam("SandiaMod")

    sapm_inverters = pvlib.pvsystem.retrieve_sam("cecinverter")

    module = sandia_modules["Canadian_Solar_CS5P_220M___2009_"]

    inverter = sapm_inverters["ABB__MICRO_0_25_I_OUTD_US_208__208V_"]

    temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
        "sapm"
    ]["open_rack_glass_glass"]

    # retreive weather data

    weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude, map_variables=True)[0]
    weather.index.name = "utc_time"

    temp_air = weather["temp_air"]
    wind_speed = weather["wind_speed"]
    pressure = weather["pressure"]

    # declare system
    system = {"module": module, "inverter": inverter, "surface_azimuth": 180}

    energies = {}

    system["surface_tilt"] = latitude
    solpos = pvlib.solarposition.get_solarposition(
        time=weather.index,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        temperature=temp_air,
        pressure=pressure,
    )
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
    dc = pvlib.pvsystem.sapm(effective_irradiance, tcell, module)
    ac = pvlib.inverter.sandia(dc["v_mp"], dc["p_mp"], inverter)
    acdp = ac.to_frame()

    acdp["utc_time"] = pd.to_datetime(acdp.index)
    acdp["utc_time"] = acdp.index.strftime("%m-%d %H:%M:%S")
    acdp.columns = ["val", "dat"]

    acdp.plot(x="dat", y="val")

    annual_energy = acdp["val"].sum()
    # plt.show()
    energies[name] = annual_energy

    energies = pd.Series(energies)

    # based on the parameters specified above, these are in W*hrs
    energy_yield = int(energies.round(0))

    return energy_yield / 1000
