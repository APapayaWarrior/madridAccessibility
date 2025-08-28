import pandas as pd
import geopandas as gpd
import os
from os import listdir
from os.path import join
import r5py
import datetime

listGTFSpaths = [
    '../gtfsData/busesEMT_9may2025.zip', # buses EMT
    '../gtfsData/metro_30may2025.zip', # metro
    '../gtfsData/metroLigero_26feb2025.zip', # metro ligero
    '../gtfsData/cercanias_23july2025_fromRenfe.zip' # cercanias
] + [join('../gtfsData/busesInterurbanos_Urbanos_all_16july2025/', i) for i in listdir('../gtfsData/busesInterurbanos_Urbanos_all_16july2025/')]

madridOSMpath = '../osmData/madrid-latest.osm.pbf' 

transport_network = r5py.TransportNetwork(
    madridOSMpath,
    listGTFSpaths,
    allow_errors=True
)

destType = 'templos'
with open('../muni2024/madridMetroArea/muniList.txt') as f:
    municipios = [i[:-6] for i in f.readlines()]

munisDone = [i[6:-4] for i in listdir(f'./timeMatrices/{destType}/')]

# print(municipios)
# print(munisDone)

for muni in municipios:
    if muni in munisDone:
        continue
    else:
        municipioOrigen = muni
        break
    

pointOrigins =gpd.read_file(f'../muni2024/madridMetroArea/{municipioOrigen}.gpkg').rename({'GRD_ID' : 'id'}, axis=1)
pointOrigins = pointOrigins.to_crs('EPSG:3035')

pointDestinations = gpd.read_file('../POIs/templos/cleaned/templosMadrid.geojson').rename({'PK' : 'id'}, axis=1)
pointDestinations = pointDestinations.to_crs('EPSG:3035')

print(f'{pointOrigins.shape[0]} origins in {municipioOrigen} ---- {pointDestinations.shape[0]} destinations')

travel_time_matrix = r5py.TravelTimeMatrix(
    transport_network= transport_network,
    origins = pointOrigins,
    destinations = pointDestinations,
    transport_modes = [r5py.TransportMode.TRANSIT],
    departure=datetime.datetime(2025, 7, 28, 14, 0, 0)
)

travel_time_matrix = pd.DataFrame(travel_time_matrix)

travel_time_matrix.to_csv(f'./timeMatrices/{destType}/desde_{municipioOrigen}.csv')

duration = 0.25  # seconds
freq = 400  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))