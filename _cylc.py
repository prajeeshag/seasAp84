import subprocess
from enum import Enum
from pathlib import Path

import typer
import yaml
from questionary import prompt

app = typer.Typer()

_take_from_answers = False


def atmDt_default(x):
    if "atmDt" in x:
        return str(x["atmDt"])
    if x["atm_res"] == "4km":
        return str(20)
    elif x["atm_res"] == "8km":
        return str(45)
    raise ValueError(f"Unknown atm_res: {x["atm_res"]}")


def set_default(key, default):
    def default_(x):
        if key in x:
            return str(x[key])

        if callable(default):
            return default(x)

        return default

    return default_


def validate_yyyymm(x):
    if len(x) != 7:
        return False
    if x[4] != "-":
        return False
    try:
        int(x[:4])
        int(x[5:])
    except ValueError:
        return False
    return True


def return_defaults(key, x):
    return _take_from_answers and key in x


config = [
    {
        "name": "only_wrf",
        "type": "confirm",
        "default": set_default("only_wrf", False),
        "message": "Is this WRF-only mode?",
        "when": lambda x: not return_defaults("only_wrf", x),
    },
    {
        "name": "initialCyclePoint",
        "type": "text",
        "default": set_default("initialCyclePoint", "2009-01"),
        "message": "Set the initial cycle point (date) (e.g., '2009-01')",
        "validate": validate_yyyymm,
        "when": lambda x: not return_defaults("initialCyclePoint", x),
    },
    {
        "name": "cycle",
        "type": "select",
        "default": set_default("cycle", "R1"),
        "message": "Select the cycle period",
        "choices": ["P1M", "R1"],
        "when": lambda x: not return_defaults("cycle", x),
    },
    {
        "name": "finalCyclePoint",
        "type": "text",
        "default": set_default("finalCyclePoint", "2009-01"),
        "message": "Set the final cycle point (date) (e.g., '2009-01')",
        "when": lambda x: x["cycle"] == "P1M"
        and not return_defaults("finalCyclePoint", x),
        "validate": validate_yyyymm,
    },
    {
        "name": "FCSTDURATION",
        "type": "text",
        "default": set_default("FCSTDURATION", "214"),
        "message": "Set the forecast duration in days (e.g., '214')",
        "validate": lambda x: x and int(x) > 5 and int(x) <= 214,
        "when": lambda x: not return_defaults("FCSTDURATION", x),
    },
    {
        "name": "NMEMBERS",
        "type": "text",
        "default": set_default("NMEMBERS", "1"),
        "message": "Set the number of ensemble members (NMEMBERS)",
        "filter": int,
        "validate": lambda x: x and int(x) > 0 and int(x) <= 25,
        "when": lambda x: not return_defaults("NMEMBERS", x),
    },
    {
        "name": "atm_res",
        "type": "select",
        "default": set_default("atm_res", "8km"),
        "message": "Set the atmospheric resolution",
        "choices": ["4km", "8km"],
        "when": lambda x: not return_defaults("atm_res", x),
    },
    {
        "name": "atmDt",
        "type": "text",
        "default": set_default("atmDt", atmDt_default),
        "message": "Set the atmospheric time step (atmDt) in seconds",
        "filter": int,
        "when": lambda x: not return_defaults("atmDt", x),
    },
    {
        "name": "ocnDt",
        "type": "text",
        "default": set_default("ocnDt", "90"),
        "message": "Set the ocean time step (ocnDt) in seconds",
        "filter": int,
        "when": lambda x: not x["only_wrf"] and not return_defaults("ocnDt", x),
    },
    {
        "name": "cpldDt",
        "type": "text",
        "default": set_default("cpldDt", "180"),
        "message": "Set the coupled model time step (cpldDt) in seconds",
        "when": lambda x: not x["only_wrf"] and not return_defaults("cpldDt", x),
    },
    {
        "name": "install_pkgs",
        "type": "confirm",
        "default": set_default("install_pkgs", False),
        "message": "Install packages?",
        "when": lambda x: not return_defaults("install_pkgs", x),
    },
]


class CylcCommands(Enum):
    vip = "vip"
    vr = "vr"


@app.command()
def main(cmd: CylcCommands, ans: str = "", defaults: bool = False):
    global _take_from_answers
    _take_from_answers = defaults

    answer_file = ans
    answers = {}
    if answer_file and Path(answer_file).exists():
        answers = yaml.safe_load(Path(answer_file).read_text())
    answers = ask_dictstyle(answers=answers)

    answers["cpuOCN"] = 238
    answers["ocnDtBal"] = 20

    workflow_name = create_workflow_name(answers)
    answer_file = f".{workflow_name}_answers.yml"
    lft = "{%"
    rht = "%}\n"
    with open("param.cylc", "w") as f:
        for k, v in answers.items():
            if k == "FCSTDURATION":
                v = f"P{v}D"
            f.write(f"{lft} set {k} = {repr(v)} {rht}")
    result = subprocess.run(["cylc", "vip", "-n", workflow_name, "--no-run-name", "."])
    return_code = result.returncode
    if return_code != 0:
        raise SystemExit(return_code)
    Path(answer_file).write_text(yaml.dump(answers))


def create_workflow_name(answers):
    wname = "CPLD"
    if answers["only_wrf"]:
        wname = "WRF"
    wrf_res = answers["atm_res"]
    wname += wrf_res
    wname += "SEAS_H"
    wname += answers["initialCyclePoint"].replace("-", "")[0:6]
    if answers["cycle"] == "P1M":
        end_date = answers["finalCyclePoint"].replace("-", "")[0:6]
        wname += f"-{end_date}"
    return wname


def ask_dictstyle(**kwargs):
    return prompt(config, **kwargs)


if __name__ == "__main__":
    app()
