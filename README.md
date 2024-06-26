# ap84SeasRF

Cylc workflow for downscaling of the seasonal reforecast for the AP region using SKRIPS coupled model


## Design rules

### The workflow should run out of the box
Design the workflow so that the only external dependencies required are the large input datasets. All other components, including parameter files (e.g., namelists), scripts, utilities (e.g., CDO, NCO), and model code (e.g., WRF, MITgcm), should be installed and configured by the workflow itself. The dependency installation and configuration should be the initial step of the workflow. Every other task should depend on the successful completion of the dependency installation.

### A clean and portable `flow.cylc`
- Define each dependency (=>) on a separate line in the `[[graph]]` section.
- Avoid including site-specific details in the main flow.cylc file. Instead, use Jinja2 include files for site-specific configurations.
- Do not use inheritance in site include files to prevent overriding any inheritance defined in the main flow.cylc.
- Keep the [runtime][root] section minimal.
- Minimize the use of Jinja2. Prefer task parameterization.
- Use `pre-script` for setting up the run directory and any pre-job configurations, such as editing namelists, and copying or linking necessary input and forcing files.
- Use `script` for the command that launches the actual job (e.g., mpirun -np3 wrf.exe).
- Use `post-script` for any post-run tasks, such as moving the outputs.
- Ensure that pre-script, script, and post-script are site-agnostic.
- The parallel job launching command in the script will be site-specific. Provide this through the site include file by setting `[[[environment]]] run_cmd` for the applicable tasks.
- Use env-script for site-specific environment loading commands (e.g., module load, mamba activate). Note: The variables defined in `[[[environment]]]` are not visible in env-script, as env-script is invoked before `[[[environment]]]`.
- Use the `cylc lint` to check the Cylc code style.
- Use `shfmt` for formatting bash scripts.
- Use the `black` formatter for Python codes.

For more information on writing workflows see the
[user guide](https://cylc.github.io/cylc-doc/stable/html/user-guide/writing-workflows/index.html).

There is also a
[workflow design guide](https://cylc.github.io/cylc-doc/stable/html/workflow-design-guide/index.html).
