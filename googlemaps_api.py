import re
import googlemaps
from datetime import datetime
gmaps = googlemaps.Client(key='AIzaSyBVaHkjw6IGtnHRaFQlP-iUdeXsBfG5PN4')

def get_Geocode(address):
    geocode_result = gmaps.geocode(address)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']
    geocode = [lat, lng]
    return geocode

def get_distance_time(orig,dest,mode):
    orig_coord = str(orig[0])+","+str(orig[1])
    dest_coord = str(dest[0])+","+str(dest[1])
    summary = gmaps.distance_matrix(orig_coord, dest_coord, mode)['rows'][0]
    distance = summary['elements'][0]['distance']['value']
    time = summary['elements'][0]['duration']['text']
#    try:
#        distance = summary['elements'][0]['distance']['value']
#    except:
#        distance = 100
#        print(orig_coord, dest_coord)
#    try:
#        time = summary['elements'][0]['duration']['text']
#    except:
#        time = '5 min'
#        print(orig_coord, dest_coord)
    final = [distance,time]
    return final

def get_address(geocode):
    reverse_geocode_result = gmaps.reverse_geocode((geocode[0], geocode[1]))
    address = reverse_geocode_result[0]['formatted_address']
    return address

#origin = get_Geocode('219 N 35th Street, Philadelphia PA')
#destination = get_Geocode('3140 Chestnut, Philadelphia PA')
#final = get_distance_time(origin,destination,'driving')
#addr = get_address([39.8680, -75.0427])
#print(origin)
#print(destination)
#print(final)
#print(addr)

