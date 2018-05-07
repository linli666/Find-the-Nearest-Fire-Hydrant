from NearestElement import *
hydrants = data_generator('/Users/Joe/Desktop/phillyCODEFEST/hydrants.json')
a = hydrants.get_nearest_fast_allinOne(-75.1, 39.9, epsilon = 0.5, top = 3, metric = 'km')
print(a)
# bounding box debugging
# lng_l, lat_u, lat_l, _, _, _ = hydrants.reduce_search_space(0.5, -75.109585, 39.951305, metric = 'km')
