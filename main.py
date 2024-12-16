import os
from openai import OpenAI
import csv
from dotenv import load_dotenv, find_dotenv
from prompts import *
from vrp import vrp_solver, format_output_with_cities
import pandas as pd
import json


# load the .env file
_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
coordinates_db = os.path.join(script_dir, "inputs", "coordinates_database.csv") 
orders = os.path.join(script_dir, "inputs", "orders.csv") 


# initialize model settings
model = "gpt-4o"
temperature = 0.2
max_tokens = 2500


# function for reading csv
def read_csv(file):
    data = []
    with open(file, "r", newline = "") as csvfile:   
        csv_reader = csv.reader(csvfile)             
        for row in csv_reader:
            data.append(row)                        
        return data
    

# apply read_csv to input csv's
sample_data = read_csv(coordinates_db)
sample_data_str = "\n".join([",".join(row) for row in sample_data])

mails = read_csv(orders)
mails_str = "\n".join([",".join(row) for row in mails])


# prompts variables for first assistant
system_message = system_message
prompt = generate_prompt(sample_data_str, mails_str)


# assistant function to execute model with prompt
def shipment_information_assistant():
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {   
                "role": "system", 
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return completion.choices[0].message.content

result = shipment_information_assistant()


# Clean up the string and convert it into a dictionary
output_cleaned = result.replace("```python\n", "").replace("\n```", "").strip()

try:
    output_dict = json.loads(output_cleaned)
except json.JSONDecodeError as e:
    print(f"Failed to parse the string as JSON: {e}")


# convert output_dict into df in order to save it as csv
df = pd.DataFrame(output_dict)

depot = pd.DataFrame({'id': [6], 'City': ['Munich'], 'Latitude': [48.13886249311937], 'Longitude': [11.508838257888504], 'Orderer': [""], 'Demand': [""]})       # since "Munich" is always our depot we have insert coordinates of it as first entry in df in order that the vrp_solver works correclty
rows = df.to_dict('records')
rows.insert(0, depot.to_dict('records')[0])                                                                                                                      # Insert the new row as the first data row (right after the header)
df = pd.DataFrame(rows)

output_file = os.path.join(script_dir, "outputs", "output.csv") 
df.to_csv(output_file, index=False)





# Immediately reading in again the output csv, set the capacity of a vehicle and execute vrp

capacity = 40

solution, df = vrp_solver(output_file, capacity)
city_routes = format_output_with_cities(solution, df)           # to replace numbers by city names


# Merge vehicles and routes into a new list
vehicles_file = os.path.join(script_dir, "inputs", "vehicles.csv") 
vehicles = read_csv(vehicles_file)
assigned_vehicles = []

for i in range(len(city_routes)):
    vehicle = vehicles[i+1]  
    route = city_routes[i]  
    assigned_vehicles.append(vehicle + [route])


# adding the names of the orderers to list of tours
data_output = read_csv(output_file)

def map_cities_to_orderers(data_output):
    """
    Create a mapping from cities to orderers.
    Assumes `data` is a list of lists with the structure:
    ['id', 'City', 'Latitude', 'Longitude', 'Orderer', 'Demand']
    """
    city_to_orderer = {row[1]: row[4] for row in data_output[1:]}               # Skip the header row

    return city_to_orderer

city_to_orderer = map_cities_to_orderers(data_output)

for tour in assigned_vehicles:
    cities = tour[3]  
    orderers = [city_to_orderer[city] for city in cities if city != 'Munich']  # set depot, in this case 'Munich'
    tour.append(orderers)  

for i in assigned_vehicles:                                                     # print all routes with respective informations
    print(i)


# create a text file with all tour information
all_tours = os.path.join(script_dir, "outputs", "all_tours.txt") 


with open(all_tours, "w") as file:
    for tour in assigned_vehicles:
        file.write(f"Vehicle ID: {tour[0]}\n")
        file.write(f"Truck Plates: {tour[1]}\n")
        file.write(f"Driver Name: {tour[2]}\n")
        file.write(f"Route: {', '.join(tour[3])}\n")
        file.write(f"Orderers: {', '.join(tour[4])}\n")
        file.write("\n" + "-"*40 + "\n\n") 





# variables for second assistant
system_message2 = system_message2
prompt2 = generate_prompt2(assigned_vehicles, mails_str)


# assistant to create order confirmation mails
def generate_mails_assistant():
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {   
                "role": "system", 
                "content": system_message2
            },
            {
                "role": "user",
                "content": prompt2
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return completion.choices[0].message.content

confirmations = generate_mails_assistant()

# save output file
confirmation_mails = os.path.join(script_dir, "outputs", "confirmation_mails.csv") 

with open(confirmation_mails, "w") as file:
    file.write(confirmations)


# print final confirmation
print("\nAssistants answer: \n")

print(confirmations)