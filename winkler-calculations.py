import time
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

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

# Only 2040 to 2060 despite file name
forecast_files = ('./agg_macav2metdata_tasmin_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_daily.nc', './agg_macav2metdata_tasmax_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_daily.nc')

# Utilities
def create_wink_vals(da): 
  func = lambda x: x - 283.15 if x >= 283.15 else 0
  return xr.apply_ufunc(func, da['air_temperature'], vectorize = True)

mean_air_temp = lambda x: (x['air_temperature_min'] + x['air_temperature_max']) / 2

def create_wink_temp(min_max_ds):
  ds_min = xr.open_dataset(min_max_ds[0]).load().rename({ 'air_temperature': 'air_temperature_min'})
  ds_max = xr.open_dataset(min_max_ds[1]).load().rename({ 'air_temperature': 'air_temperature_max'})
  seasonal_ds_min = ds_min.sel(time = (ds_min['time.month'] >= 4) & (ds_min['time.month'] <= 10))
  seasonal_ds_max = ds_max.sel(time = (ds_max['time.month'] >= 4) & (ds_max['time.month'] <= 10))
  seasonal_ds = (xr.merge([seasonal_ds_min, seasonal_ds_max])
    .assign(air_temperature = mean_air_temp)
    .drop_vars(['air_temperature_min', 'air_temperature_max'])
    .assign(wink_temperature = create_wink_vals))
  return seasonal_ds['wink_temperature'].resample(time='Y').sum().to_dataset()

def assign_wink_region(da): 
  def find_region(x):
    if x == 0:
      return -1
    elif x < 850:
      return 0
    elif (x >= 850) & (x < 1111):
      return 1
    elif (x >= 1111) & (x < 1389):
      return 1.5
    elif (x >= 1389) & (x < 1668):
      return 2
    elif (x >= 1668) & (x < 1945):
      return 3
    elif (x >= 1945) & (x < 2223):
      return 4
    elif (x >= 2223) & (x < 2700):
      return 5
    else: 
      return 6
  return xr.apply_ufunc(find_region, da['wink_temperature'], vectorize = True)

# Run Historical Analysis
historical_dataset = xr.Dataset()
for result in [create_wink_temp(pair) for pair in historical_files]:
  historical_dataset = xr.merge([historical_dataset, result])
historical_dataset = (historical_dataset.median(dim=['time'])
  .assign(wink_region = assign_wink_region))

plt.show(historical_dataset['wink_region'].plot.hist())
historical_dataset.to_netcdf(path='./winkler-regions_and_medians_1980-1999.nc')
print(historical_dataset)

# Run Forecast Analysis
forecast_2050_dataset = (create_wink_temp(forecast_files)
  .median(dim=['time']).assign(wink_region = assign_wink_region))
plt.show(forecast_2050_dataset['wink_region'].plot.hist())
forecast_2050_dataset.to_netcdf(path='./winkler-regions_and_medians_2040-2060.nc')
