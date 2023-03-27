import requests
import json
import datetime
import sys
from prettytable import PrettyTable

URL_PREFIX = 'https://www.atcofficial.com/api/commerce/inventory/stock/?itemId='
ALL_VIP_JSON = 'allvip.json'

def get_arguments():
    try:
        option = sys.argv[1].lower()
    except:
        option = "r"
    try:
        city = sys.argv[2].lower()
    except:
        city = "eu"
    return (option, city)

def get_json(option, city):
    alljson = open_json(ALL_VIP_JSON)
    shows = []
    if (option == 'all'):
        shows = alljson
    elif (option == 'r'):
        shows = list(filter(lambda x : city in x["region"], alljson))
    elif (option == 'c'): 
        shows = list(filter(lambda x : city in x["city"].lower(), alljson))
    else:
        raise Exception("options available => c = city / r = region / all")
    return shows

def open_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)       
    
def main():
    (option, city) = get_arguments()
    shows = get_json(option, city)
    table = PrettyTable()
    table.field_names = ["City", "Quantity", "Last Updated"]
    print("Generating table...")
    for show in shows:
        url = f"{URL_PREFIX}{show['itemId']}"
        response = requests.get(url)
        new_quantity = get_quantity(response)
        if new_quantity >= 0:
            date_format = "%d/%m/%y - %H:%M UTC" if show["region"] == 'eu' else "%m/%d/%y - %H:%M UTC" 
            show["lastUpdated"] = datetime.datetime.utcnow().strftime(date_format)
            show["quantity"] = new_quantity
        table.add_row([show["city"], show["quantity"], show["lastUpdated"]])
    table.sortby = "Quantity"
    print(table)
    write_json(shows)

def write_json(shows):
    all_json = open_json(ALL_VIP_JSON)
    for show in shows:
        for i in range(len(all_json)):
            if all_json[i]["city"] == show["city"]:
                all_json[i].update(show)
    json_string = json.dumps(all_json, default=str)
    with open(ALL_VIP_JSON, "w") as f:
        f.write(json_string)

    
def get_quantity(response):
    quantity = -1
    try:
        json_data = json.loads(response.text)
        quantity = json_data["results"][0]["qtyInStock"]
        return quantity
    except:
        return quantity
    
main()