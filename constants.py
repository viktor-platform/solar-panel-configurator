'''Dictionaries describing module and inverter information are stored here'''

type_dict = {
            "California Energy Commission": "cecinverter",
            "Sandia National Laboratories": "sandiainverter",
        }
module_name_dict = {
            "AstroPower APX-120": {
                "name": "AstroPower APX-120 [ 2001]",
                "price": 240.81,
            },
            "BP Solar SX160B": {
                "name": "BP Solar SX160B [2005 (E)]",
                "price": 430.74,
            },
            "Kyocera Solar PV110": {
                "name": "Kyocera Solar PV110 [2003 (E)]",
                "price": 271.69,
            },
            "Mitsubishi PV - MF185UD4": {
                "name": "Mitsubishi PV-MF185UD4 [2006 (E)]",
                "price": 154.52,
            },
            "Sanyo HIP - 200BE11": {
                "name": "Sanyo HIP-200BE11 [2006 (E)]",
                "price": 525.01,
            },
            "Sharp ND - L3E1U": {
                "name": "Sharp ND-L3E1U [2002 (E)]",
                "price": 675.00
            },
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
            "ABB: PVI-0.3 Inverter": {  # First three CEC Inverters
                "name": "ABB: PVI-3.0-OUTD-S-US-A [240V]",
                "price": 173.19,
            },
            "Outback Power Tech. Inverter": {
                "name": "OutBack Power Technologies - Inc : GS8048A [240V]",
                "price": 3797.88,
            },
            "Hanwa Q-Cells Inverter": {
                "name": "Hanwha Q CELLS America Inc : Q.HOME+ AC-G1-8.6 [240V]",
                "price": 1877.47,
            },
            "Generac Power Systems Inverter": {  # Second three Sandia Inverters
                "name": "Generac Power Systems: XVT076A03 [240V]",
                "price": 3431.35,
            },
            "Delta Electronics Inverter": {
                "name": "Delta Electronics: E4-TL-US(AC) [240V]",
                "price": 2589.40,
            },
            # "Chint Power Systems Inverter": {
            #     "name": " Chint Power Systems America: CPS SCA5KTL-O US [240V]",
            #     "price": 1616.45,
            # },
            "Enphase Energy Inc Inverter": {
                "name": "Enphase Energy Inc : IQ6-60-5-US [240V]",
                "price": 220.95,
            },

        }
