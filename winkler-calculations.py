import xarray as xr

# Planned Steps
# (1) isolate the days between April 1 through October 31
# (2) average tasmin and tasmax
# (3) for each day, every degree above 10°C is added to an index
# (4) the index is averaged across the climate period.

files = [
  '../macav2metdata_tasmin_CCSM4_r6i1p1_historical_1980_1984_CONUS_daily.nc' # set as min, max tuples once loaded
]

ds = xr.open_dataset(files[0])
seasonal_ds = ds.sel(time=(ds['time.month'] >= 4) & (ds['time.month'] <= 10)) # Step 1
seasonal_ds = seasonal_ds.assign(wink_temperature = lambda x: x.air_temperature - 283.15) # Kelvin conversion + 10°C growing season constraint
