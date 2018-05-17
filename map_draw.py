import json, urllib2, webbrowser
from gmplot import gmplot
from bus_url import *
from bus_streets import *

# List of variables needed for the execution of the code
API_KEY = 'AIzaSyBAG6CASjfND1ApXO65d7mtpuP8Cty4fdc'
color = ['red','blue','green','yellow','black']

# Search for the origin and destination
# Get valid transport which includes both origin and destination
# Get index of each street in the list
def search_street(origin, destination):
    valid_transport = []
    valid_indexs = []
    for i in range(len(bus_str)):
        found_locations = []
        valid = 0
        for j in range (len(bus_str[i])):
            if str(bus_str[i][j]) == str(origin) or str(bus_str[i][j]) == str(destination):
                valid = valid + 1
                found_locations.append(j)
        if valid == 2:
            valid_transport.append(i)
            valid_indexs.append(found_locations)
    return valid_transport, valid_indexs

# Finds shortest route out of all routes
def find_shortest(valid_transport, valid_index):
    difference = []
    for i in range (len(valid_index)):
        diff = valid_index[i][1]-valid_index[i][0]
        difference.append(diff)
    try:
        min_index = difference.index(min(difference))
        fastest_transport = valid_transport[min_index]
    except Exception as e:
        print "No valid transport for your locations"
        fastest_transport = "NONE"
    #fastest_transport = valid_transport[min_index]
    return fastest_transport

# Use Google API and get url for further use
def route_url(API_KEY, bus_num):
    url = urllib2.urlopen(bus_url[bus_num].format(API_KEY))
    route_url_data = json.load(url)
    return route_url_data

# Gets list of coordinates from the given url
def get_locations(route_url_data,API_KEY):
    start_location = []
    #print route_url_data
    for i in range(len(route_url_data['routes'][0]['waypoint_order'])+1):
        for element in route_url_data['routes'][0]['legs'][i]['steps']:
            start_location.append([element['start_location']['lat'], element['start_location']['lng'],'|'])
            start_location.append([element['end_location']['lat'], element['end_location']['lng'],'|'])
    #print start_location
    locations = []
    for i in start_location[1::2]:
        locations.append(str(i[0]) + ',' + str(i[1]) + str(i[2]))
    return locations

# Gets valid link for the plotting
def get_road_data(locations,API_KEY):
    url = ('https://roads.googleapis.com/v1/snapToRoads?path={}&interpolate=true&key={}'.format(''.join(locations), API_KEY))
    url = url.rsplit('|',1)
    url = ''.join(url)
    url = urllib2.urlopen(url)

    url_data = json.load(url)

    roads = []
    for elem in url_data['snappedPoints']:
        roads.append((elem['location']['latitude'], elem['location']['longitude']))
    return roads

# Plots the routes of the valid transport
def plot(road_draw, valid_transport, color):
    gmap = gmplot.GoogleMapPlotter.from_geocode("Yerevan")
    for i in range (len(valid_transport)):
        place_lats, place_lons = zip(*road_draw[i])
        gmap.plot(place_lats, place_lons, color[i], edge_width=10)
        gmap.draw("my_map.html")

def main():
    print "<-<-<-<-< Welcome to TranspoRoute >->->->->"
    origin = raw_input("Input your origin point: ").title()
    destination = raw_input("Input your destination point: ").title()
    valid_transport, valid_index = search_street(origin, destination)
    valid_transport_str = ''
    for i in range (len(valid_transport)):
        valid_transport_str = valid_transport_str + str(valid_transport[i]) + ', '
    valid_transport_str = valid_transport_str[:len(valid_transport_str)-2]
    print "You can use bus/buses " + valid_transport_str + " to get from " + origin + " to " + destination
    fastest_transport = find_shortest(valid_transport, valid_index)
    print "Bus which will help you get from " + origin + " to " + destination + " in the shortest time is #" + str(fastest_transport)
    #print "Fastest bus route is marked on the map in <<" + color[valid_transport.index(fastest_transport)] + ">>"
    road_draw = []
    for i in range (len(valid_transport)):
        bus_num = valid_transport[i]
        route_url_data = route_url(API_KEY, bus_num)
        locations = get_locations(route_url_data, API_KEY)
        roads = get_road_data(locations, API_KEY)
        road_draw.append(roads)
    plot_check = 0
    e = ""
    while plot_check != 1:
        try:
            plot(road_draw, valid_transport, color)
        except Exception as e:
            continue
            #print "Wait a little bit"
        if e != "list index out of range":
            plot_check = 1
    webbrowser.open_new_tab("my_map.html")
    print "Your default browser should open the map with the routes, if not, please check browser settings or open file 'my_map.html', which is in the same location as the python file"

main()