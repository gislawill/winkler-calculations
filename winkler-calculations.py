import xarray as xr
import numpy as np

# Planned Steps
# (1) isolate the days between April 1 through October 31
# (2) average tasmin and tasmax
# (3) for each day, every degree above 10°C is added to an index
# (4) the index is averaged across the climate period.

files = [
  './macav2metdata_tasmin_CCSM4_r6i1p1_historical_1980_1984_CONUS_daily.nc' # set as min, max tuples once loaded
]

# Utils
def to_wink_val(kelvin_val): # Kelvin conversion + 10°C growing season constraint
  if (np.isnan(kelvin_val)):
    return kelvin_val
  elif (kelvin_val >= 283.15):
    return kelvin_val - 283.15
  else:
    return 0

def create_wink_vals(da): # Vectorize logic 
  return xr.apply_ufunc(to_wink_val, da['air_temperature'], vectorize=True)

ds = xr.open_dataset(files[0]).load()
seasonal_ds = ds.sel(time = (ds['time.month'] >= 4) & (ds['time.month'] <= 10)) # Step 1
seasonal_ds = seasonal_ds.assign(wink_temperature = create_wink_vals)
seasonal_ds['wink_temperature'].resample(time='M').sum()