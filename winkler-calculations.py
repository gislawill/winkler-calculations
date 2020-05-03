import time
import xarray as xr
import numpy as np

# Planned Steps
# (1) isolate the days between April 1 through October 31
# (2) average tasmin and tasmax
# (3) for each day, every degree above 10°C is added to an index
# (4) the index is averaged across the climate period.

historical_files = [
  ('./macav2metdata_tasmin_CCSM4_r6i1p1_historical_1980_1984_CONUS_daily.nc', './macav2metdata_tasmax_CCSM4_r6i1p1_historical_1980_1984_CONUS_daily.nc'),
  ('./macav2metdata_tasmin_CCSM4_r6i1p1_historical_1985_1989_CONUS_daily.nc', './macav2metdata_tasmax_CCSM4_r6i1p1_historical_1985_1989_CONUS_daily.nc'),
  ('./macav2metdata_tasmin_CCSM4_r6i1p1_historical_1990_1994_CONUS_daily.nc', './macav2metdata_tasmax_CCSM4_r6i1p1_historical_1990_1994_CONUS_daily.nc'),
  ('./macav2metdata_tasmin_CCSM4_r6i1p1_historical_1995_1999_CONUS_daily.nc', './macav2metdata_tasmax_CCSM4_r6i1p1_historical_1995_1999_CONUS_daily.nc')
]

# Utilities
def create_wink_vals(da): 
  func = lambda x: x - 283.15 if x >= 283.15 else 0
  return xr.apply_ufunc(func, da['air_temperature'], vectorize = True)

mean_air_temp = lambda x: (x['air_temperature_min'] + x['air_temperature_max']) / 2

historical_dataset = xr.Dataset()

for pair in historical_files:
  ds_min = xr.open_dataset(pair[0]).load().rename({ 'air_temperature': 'air_temperature_min'})
  ds_max = xr.open_dataset(pair[1]).load().rename({ 'air_temperature': 'air_temperature_max'})
  seasonal_ds_min = ds_min.sel(time = (ds_min['time.month'] >= 4) & (ds_min['time.month'] <= 10))
  seasonal_ds_max = ds_max.sel(time = (ds_max['time.month'] >= 4) & (ds_max['time.month'] <= 10))
  seasonal_ds = (xr.merge([seasonal_ds_min, seasonal_ds_max])
    .assign(air_temperature = mean_air_temp)
    .drop_vars(['air_temperature_min', 'air_temperature_max']))
  seasonal_ds = seasonal_ds.assign(wink_temperature = create_wink_vals)
  xr.merge([historical_dataset, seasonal_ds['wink_temperature'].resample(time ='Y').sum()])

print(historical_dataset)