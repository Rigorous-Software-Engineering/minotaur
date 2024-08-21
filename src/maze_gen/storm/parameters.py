"""
Copyright 2020 MPI-SWS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from termcolor import colored


def get_supported_theories(solver):
    theories =  {
                    "z3" : ["ALIA", "AUFNIA", "LRA", "QF_ALIA", "QF_AUFNIA", "QF_LRA", "QF_RDL", "QF_UFIDL",
                   "QF_UFNRA", "UFDTLIA", "AUFDTLIA", "AUFNIRA", "NIA", "QF_ANIA", "QF_AX", "QF_FP", "QF_NIA",
                    "QF_UFLIA", "UFLIA", "AUFLIA", "BV", "NRA", "QF_AUFBV", "QF_BV", "QF_IDL", "QF_NIRA",
                   "QF_UF", "QF_UFLRA", "UF", "UFLRA", "AUFLIRA", "LIA", "QF_ABV", "QF_AUFLIA", "QF_BVFP",
                   "QF_LIA", "QF_NRA", "QF_UFBV", "QF_UFNIA", "UFDT", "UFNIA", "QF_S"],

                "yices": ["QF_ABV", "QF_ALIA", "QF_AUFBV", "QF_AUFLIA", "QF_AX", "QF_BV", "QF_IDL", "QF_LIA", "QF_LIRA",
                  "QF_LRA", "QF_NIA", "QF_NIRA", "QF_NRA", "QF_RDL", "QF_UF", "QF_UFBV", "QF_UFIDL", "QF_UFLIA",
                  "QF_UFLRA", "QF_UFNIA", "QF_UFNIRA", "QF_UFNRA", "LRA",
                  "UFLRA"],

                "z3str3" : ["QF_S"],

                "smtinterpol" : ["QF_ABV", "QF_ALIA", "QF_AUFBV", "QF_AUFLIA", "QF_AX", "QF_BV", "QF_IDL", "QF_LIA", "QF_LIRA",
                  "QF_LRA", "QF_NIA", "QF_NIRA", "QF_NRA", "QF_RDL", "QF_UF", "QF_UFBV", "QF_UFIDL", "QF_UFLIA",
                  "QF_UFLRA", "QF_UFNIA", "QF_UFNIRA", "QF_UFNRA", "LRA",
                  "UFLRA"],

                "cvc4": ["ALIA", "AUFNIA", "LRA", "QF_ALIA", "QF_AUFNIA", "QF_LRA", "QF_RDL", "QF_UFIDL",
                   "QF_UFNRA", "UFDTLIA", "AUFDTLIA", "AUFNIRA", "NIA", "QF_ANIA", "QF_AX", "QF_FP", "QF_NIA",
                    "QF_UFLIA", "UFLIA", "AUFLIA", "BV", "NRA", "QF_AUFBV", "QF_BV", "QF_IDL", "QF_NIRA",
                   "QF_UF", "QF_UFLRA", "UF", "UFLRA", "AUFLIRA", "LIA", "QF_ABV", "QF_AUFLIA", "QF_BVFP",
                   "QF_LIA", "QF_NRA", "QF_UFBV", "QF_UFNIA", "UFDT", "UFNIA", "QF_S"],

                "mathsat" : ["QF_ABV", "QF_ABVFP", "QF_ABVFPLRA", "QF_ALIA", "QF_ANIA", "QF_AUFBV", "QF_AUFLIA",
                             "QF_AUFNIA", "QF_AX", "QF_BV", "QF_BVFP", "QF_BVFPLRA", "QF_FP", "QF_FPLRA", "QF_IDL",
                             "QF_LIA", "QF_LIRA", "QF_LRA", "QF_NIA", "QF_NIRA", "QF_NRA", "QF_RDL", "QF_UF", "QF_UFBV",
                             "QF_UFFP", "QF_UFIDL", "QF_UFLIA", "QF_UFLRA", "QF_UFNIA", "QF_UFNRA"],

                "bitwuzla" : ["BV", "QF_ABV", "QF_ABVFP", "QF_AUFBV", "QF_BV", "QF_BVFP", "QF_FP", "QF_UFBV", "QF_UFFP"]

    }
    return theories[solver]


parameters = {
        "max_depth": 20,
        "max_assert": 20,
        "enrichment_steps": 1000,
        "number_of_mutants": 1000,
        "mutant_generation_timeout" : 900, # 15 mins
        "mutant_running_timeout" : 900, # 15 mins
        "solver_timeout" : 120,
        "check_sat_using" : ["yes", "no"],  # remove an option if you want a single mode. Otherwise storm will choose with a prob
        "check_sat_using_options" : ["horn", "(then horn-simplify default)", "dom-simplify", "(then dom-simplify smt)"],
        "incremental": ["yes", "no"]    # remove an option if you want a single mode. Otherwise storm will choose with a prob
    }




def get_parameters_dict(replication_mode, bug_number):
    if not replication_mode:
        print("#######" + colored(" Getting the normal fuzzing parameters", "magenta", attrs=["bold"]))
        print(str(parameters))
        return parameters
    print("Please enter a valid bug number")
    return {}

