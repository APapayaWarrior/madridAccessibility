import pandas as pd
import geopandas as gpd
import os
import sys
from datetime import datetime, time
from os import listdir
from os.path import join
import r5py
from r5py import TransportMode


def definingOrigin():
    municipioOrigen = 0

    munisDone = [i[6:-4] for i in listdir(f'./timeMatrices/{destType}/')]

    # print(municipios)
    # print(munisDone)

    for muni in municipios:
        if muni in munisDone:
            continue
        else:
            municipioOrigen = muni
            break

    return municipioOrigen
   
def main(municipioOrigen):

    if municipioOrigen == 0:
        prtStr = 'all origins processed ' + '-' * 10 + datetime.now().strftime("%I:%M%p")
        print(prtStr.rjust(30, '-'))
        return -1

    pointOrigins =gpd.read_file(f'../muni2024/madridMetroArea/{municipioOrigen}.gpkg').rename({'GRD_ID' : 'id'}, axis=1)
    pointOrigins = pointOrigins.to_crs('EPSG:3035')

    pointDestinations = gpd.read_file('../POIs/educacion/cleaned/centrosEducativos_secundaria.geojson').rename({'centro_codigo' : 'id'}, axis=1)
    pointDestinations = pointDestinations.to_crs('EPSG:3035')

    print(f'{datetime.today().strftime("%I:%M%p")} : {pointOrigins.shape[0]} origins in {municipioOrigen} ---- {pointDestinations.shape[0]} destinations')

    travel_time_matrix = r5py.TravelTimeMatrix(
        transport_network= transport_network,
        origins = pointOrigins,
        destinations = pointDestinations,
        transport_modes = [TransportMode.TRANSIT, TransportMode.WALK, TransportMode.TRAM, TransportMode.SUBWAY, TransportMode.RAIL, TransportMode.BUS],
        access_modes = [TransportMode.WALK],
        departure = datetime(2025, 7, 28, 14, 0, 0)
    )

    travel_time_matrix = pd.DataFrame(travel_time_matrix)

    travel_time_matrix.to_csv(f'./timeMatrices/{destType}/desde_{municipioOrigen}.csv')

    return 0


if __name__ == '__main__':

    print('building transport network...', end = '')

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

    sys.stdout.flush()
    print('\rfinding next origins...'.ljust(50, ' '))

    destType = 'secundaria'
    with open('../muni2024/madridMetroArea/muniList.txt') as f:
        municipios = [i[:-6] for i in f.readlines()]
    
    done = False
    while not done:
        muni = definingOrigin()
        x = main(muni)
        if x == -1:
            done = True

    duration = 0.25  # seconds
    freq = 400  # Hz
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
    
