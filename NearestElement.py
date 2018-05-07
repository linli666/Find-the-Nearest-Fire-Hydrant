import pandas
import json
from math import radians, cos, sin, asin, sqrt, pi, degrees
from googlemaps_api import *
class data_generator(object):
    """Load, integrate and digest data from a given path:

    Attributes:
        path: A string representing the data path
    """

    def __init__(self, path = 'hydrants.json'):
        """Return a data_generator object whose path is *path* 
           and data is a list of dictionaries.
        """
        self.path = path
        self.data = json.load(open(self.path))
        self.rearrange_data()
        
    def present_one(self, idx):
        """print a dictionary that contains the info of one element 
           (info list: *Critial*, *CriticalNotes*, 
                       *OutOfService*, *lat*, *lng*)
        """
        print(self.data[idx])

    def rearrange_data(self):
        """rearrange the data so that each element is assigned 
           an unique hash key and extract lng and lat info to 
           form two list x_lng and y_lat. These two list are ordered 
           such that the index of a pair of geocode correspond to the 
           hash key of the element.
        """
        self.data_hashed = {}
        for i, info in enumerate(self.data):
            self.data_hashed[i] = info
        self.x_lng = [0 for i in range(len(self.data))]
        self.y_lat = [0 for i in range(len(self.data))]
        for key in self.data_hashed:
            self.x_lng[key] = self.data_hashed[key]['lng']
            self.y_lat[key] = self.data_hashed[key]['lat']
        self.key_list = list(self.data_hashed.keys())
        
    def haversine(self, lng1, lat1, lng2, lat2, metric = 'km'):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        source: https://en.wikipedia.org/wiki/Haversine_formula
        """
        # convert decimal degrees to radians 
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

        # haversine formula 
        dlng = lng2 - lng1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a)) 
        if metric == 'km':
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        elif metric == 'mile':
            r = 3956
        else:
            r = 6371
        return c * r
    
    def reduce_search_space(self, epsilon, px, py, metric = 'km'):
        '''
        reduce the search space by a bounding factor epsilon, 
        this epsilon is used to restrict the x and y axis indivisually.
        '''
        if metric == 'km':
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        elif metric == 'mile':
            r = 3956
        else:
            r = 6371
        px, py = map(radians, [px, py])
        # longtitue bound
        lng_u = abs(2*asin(sin(epsilon/(2*r))/cos(py))) + px
        lng_l = px - abs(2*asin(sin(epsilon/(2*r))/cos(py)))
        # latitude bound
        lat_u = 2*asin(sin(epsilon/(2*r))) + py
        lat_l = py - 2*asin(sin(epsilon/(2*r)))
        lng_u, lng_l, lat_u, lat_l = map(degrees, [lng_u, lng_l, lat_u, lat_l])
        x_lng_reduced = []
        y_lat_reduced = []
        key_list = []
        for idx, x in enumerate(self.x_lng):
            if x >= lng_l and x <= lng_u and self.y_lat[idx] >= lat_l and self.y_lat[idx] <= lat_u:
                x_lng_reduced.append(x)
                y_lat_reduced.append(self.y_lat[idx])
                key_list.append(idx)
                
        return lng_u, lng_l, lat_u, lat_l, x_lng_reduced, y_lat_reduced, key_list
    
    
#     def find_nearest(self, px, py, x_lng_reduced = self.x_lng, y_lat_reduced = self.y_lat, key_list = self.key_list, top = 3):
    def find_nearest(self, px, py, x_lng_reduced, y_lat_reduced, key_list, top = 3, metric = 'km', d_method = 'hev'):
        
        """
        find the nearest best element given a position. 
        First find out top 3 (by default) nearest element, 
        then among those element, findout the closest 
        InService element without CriticalNotes
        (need to get clarified later)
        """
#       - for test use:
#         x_lng_reduced = self.x_lng
#         y_lat_reduced = self.y_lat
#         key_list = self.key_list
        
        min_dist = [4*pi*6371 for i in range(top)]
        min_dist_idx = [-1 for i in range(top)]
        for i in range(len(x_lng_reduced)):
            lng1 = x_lng_reduced[i]
            lat1 = y_lat_reduced[i]
            if d_method == 'hev':
                d = self.haversine(lng1, lat1, px, py, metric)
            elif d_method == 'walking':
                d = get_distance_time([lat1, lng1],[py, px],'walking')[0]
            elif d_method == 'driving':
                d = get_distance_time([lat1, lng1],[py, px],'driving')[0]
            else:
                d = self.haversine(lng1, lat1, px, py, metric)
            if d < min_dist[top-1]:
                min_dist[top-1] =  d
                min_dist_idx[top-1] = key_list[i]
                min_dist, min_dist_idx = (list(t) for t in zip(*sorted(zip(min_dist, min_dist_idx))))
#        for idx, i in enumerate(min_dist_idx):
#            if self.data_hashed[i]['OutOfService'] is False and self.data_hashed[i]['Critical'] is False:
#                return min_dist[idx], min_dist_idx[idx]
#        print('No element is in service on top', top, 'nearest spot')
#        return False
        return min_dist, min_dist_idx

    def get_nearest_fast_allinOne(self, px, py, epsilon = 1, top = 3, metric = 'km', d_method = 'walking'):
        """
        find the nearest best element given a position. 
        First find out top 3 (by default) nearest element, 
        then among those element, findout the closest 
        InService element without CriticalNotes
        (need to get clarified later)
        """
        _, _, _, _, x_lng_reduced, y_lat_reduced, key_list = self.reduce_search_space(epsilon, px, py, metric)
#        d, key = self.find_nearest(px, py, x_lng_reduced, y_lat_reduced, key_list, top, metric)
#        for i in self.data_hashed[key]:
#            print(i, '--', self.data_hashed[key][i])
#        print('distance:', d)
        min_dist, min_dist_idx = self.find_nearest(px, py, x_lng_reduced, y_lat_reduced, key_list, top, metric, d_method)
        output_med = {}
        for idx, i in enumerate(min_dist_idx):
            if i != -1:
                if self.data_hashed[i]['OutOfService'] is False:
                    output_med[idx] = self.data_hashed[i]
                
        output_pd = pandas.DataFrame.from_dict(output_med, orient='index')
        output_pd.rename(columns={'lat':'Lat','lng':'Lon'}, inplace = True)
        if len(output_pd) == 0:
            output_pd = pandas.DataFrame(columns=('Lat', 'Lon', 'OutOfService', 'Critical', 'CriticalNotes'))
        return output_pd
