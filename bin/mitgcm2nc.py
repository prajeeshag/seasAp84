#!/usr/bin/env python3

from xmitgcm import open_mdsdataset
import typer

app = typer.Typer()

@app.command()
def write_to_nc(prefix: str, startdate: str, dt: int):
    ds = open_mdsdataset(
        "./",
        geometry="curvilinear",
        delta_t=dt,
        ref_date=startdate,
        prefix=[
            prefix,
        ],
    )
    
    for var_name in ds.data_vars:
      var = ds[var_name]
      encode = {
          var_name: {
              "zlib": True,
              "complevel": 1,
              "shuffle": True,
              "fletcher32": True,
              "chunksizes": tuple(map(lambda x: x // 10, var.shape)),
          }
      }
      var.to_netcdf(f'{var_name}_{prefix}.nc', encoding=encode)
    

if __name__ == "__main__":
    app()
