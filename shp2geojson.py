"""CSSP Brazil
.. module:: shp2geojson
    :platform: Unix
    :synopsis: Batch Script for processing muncipalities
.. moduleauther: Dan Ellis & Helen Burns @ CEMAC (UoL)
.. description: This module was developed by CEMAC as part of the CSSP Brazil
   Project. This Script converts a shape file of muncipalities areas in json format
   so they can be plotted on a web map.
   :copyright: © 2022 University of Leeds.
   :license: GPL-3.0
Example:
    To use::
        python app.py
        It is best to run this app via a web server gunicorn or Apache
.. AgroClimatic-Monitor:
   https://github.com/cemac/AgroClimatic-Monitor
"""
'''
Creates a geojson file from a the Shapefiles
We then apply a simplification to the polygons

Author: D.Ellis
'''

import geopandas as gpd
import pandas as pd
import config as cf

# print(vars(cf))

encoding = 'iso-8859-1'#'ISO-8859-1'


print(cf.DATA)
brazil = gpd.read_file(cf.DATA+'shapefile/BR_borders/BR_MUN_WGS84.shp',encoding='iso-8859-1')

# brazil=brazil[[type(q)!=type(None) for q in  brazil['NOME']]]

codes = pd.read_csv(cf.DATA+'GEOCODES.csv',encoding='iso-8859-1').set_index('GEOCODE')['name'].to_dict()


both = set(brazil['GEOCODIGO'].astype(int)) & set(codes.keys())

print(len(both)- len(brazil['GEOCODIGO']))

brazil = brazil[[q in both for q in  brazil['GEOCODIGO'].astype(int)]]
brazil['id'] = [codes[int(i)] for i in brazil['GEOCODIGO']]



ids = brazil.to_crs({'init':'epsg:3857'}).geometry.area.sort_values(ascending=False).index
brazil = brazil.loc[ids]
# brazil.to_file('BR_MUN_WGS84.geojson', driver='GeoJSON')


print(brazil.loc[ids[:1000]]['id'])


'''
Simplify for Plotting
'''
print('simplifying')
import topojson as tp
topo = tp.Topology(brazil, prequantize=False)
simple = topo.toposimplify(2).to_gdf()



#
# import matplotlib.pyplot as plt
# simple.plot()
# plt.show()
# simple.geometry = simple.geometry.scale(xfact=0.9, yfact=0.9, zfact=1.0)#, origin=(0, 0))

simple.to_file(cf.PROCESSED+'geojson/web_simplified.geojson', driver='GeoJSON', encoding='utf8')


simple['GEOCODIGO id MESOREGIAO MICROREGIA LATITUDE LONGITUDE'.split()].set_index('GEOCODIGO').to_csv(cf.PROCESSED+'geojson/locinfo.csv')


def getxy(i):
    x,y = i.exterior.coords.xy
    return [list(x),list(y)]

x = list(map(getxy, brazil['geometry']))

## plotting shapes
search = simple['GEOCODIGO id MESOREGIAO MICROREGIA'.split()]
search['poly']=x
search.set_index('GEOCODIGO').to_csv(cf.PROCESSED+'geojson/poly.csv')




search = simple['id GEOCODIGO'.split()]
search.columns = ['key', 'val']

search.set_index('key').to_csv(cf.PROCESSED+'geojson/search.csv')

search = simple['id GEOCODIGO'.split()]
search.columns = ['key', 'val']




# simple.to_file('web_simplified_2.geojson', driver='GeoJSON')

'''
iconv -f ISO-8859-1 -t UTF-8 file.php > file-utf8.php

iconv -t UTF-8 counties.geojson > counties.geojson

'''
