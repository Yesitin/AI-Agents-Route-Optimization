system_message = """
        You are the assistant of a transport manager who dispatches a lot of truck transport across europe.
        During the day a lot of mail are incoming and some of them are transport orders. Your task is to recognize and filter out
        the mails which are orders. Work precisely!
"""


def generate_prompt(coordinates_db, orders):
    prompt = f"""
        During the day a lot of mail are incoming and some of them are transport orders. Your task is to recognize and filter out the mails which are orders. Pay attention to detail. You will find the mails here: {orders}. 
        Some mails are not orders, so filter them out carefully. The shipment departs from a depot (which is not mentioned) and goes to the destination city.

        1. Extract only the orders with clear shipment requests. e.g.: 2024-08-20,Wong Inc,Hello could you please send truck to Heidelberg with 8t? -- but the following is no order: 2024-08-20,Wong Inc,Hi where is truck we want to unload!? 
        2. Correct any minor typos in city names and match them with the closest name in {coordinates_db}.
        3. For each valid order, match the destination city with its coordinates from {coordinates_db}.
        4. Create a dictionary (id, cities, latitude, longitude, name of respective orderer and the number of demand) with the following structure:

        {{"id": [1, 2], "City": ["Brno", "Berlin"], "Latitude": [49.209676203025786, 52.527621645118415], "Longitude": [16.604015435659942, 13.337518138635536], "Orderer": ["Park Ltd.", "Josef KG"], "Demand": [4, 7]}}

        The number of "id"s should correspond to the number of unique cities in the orders. Provide only the dictionary as output, nothing else.



        
    """
    return prompt

############################################################

system_message2 = """
    You are the assistant of a transport manager who dispatches a lot of truck transport across europe.
    During the day a lot of mail are incoming and some of them are transport orders. Your colleague already
    created routes and your job is to send to the ordering company a confimation mail. 
"""

def generate_prompt2(assigned_vehicles, orders):
    prompt2 = f"""
        During the day a lot of mail are incoming and some of them are transport orders. Your collegaue 
        already created some tours with a central depot then some delievery point and returning to depot.
        He created a list which looks like this: 
        You get here ({assigned_vehicles}) all routes. Each sublist is a route driven by a vehicle. It contains the VehicleID, the plate numbers
        of the vehicle, the name of the driver, a list of sequential delivery points (the first and last point is the depot which is in our case Munich) and a list
        of orderers which made a order for one delivery point.

        For example: [['1', 'GRV-1234', 'Torben Nightshade', ['Munich', 'Graz', 'Klagenfurt', 'Ibiza', 'Basel', 'Munich'], ['Windfeld', 'Turner-Kingsley', 'Morris-Baker', 'Anderson']]]

        You job is now to formulate to each orderer a short, kind and professional confirmation mail where you confirm the transport. It should contain the truck plates, driver name and the tons he requested. You can find the demanded tons and exact order
        from the orderer here: {orders}. You can only make confirmation when the orderer is contained in {assigned_vehicles}.
    """
    return prompt2