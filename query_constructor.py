import re

locations = ["New York", "Tokyo"]
room_types = ["king bed", "queen bed", "suite", "single room"]
amenities = ["Wi-Fi", "pool", "free breakfast", "parking", "gym"]

def extract_location(query):
    for location in locations:
        if location.lower() in query.lower():
            return location
    return None

def extract_price_range(query):
    match = re.search(r'\$(\d+)\s*-\s*\$(\d+)', query)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None

def extract_room_type(query):
    for room_type in room_types:
        if room_type.lower() in query.lower():
            return room_type
    return None

def extract_amenities(query):
    found_amenities = []
    for amenity in amenities:
        if amenity.lower() in query.lower():
            found_amenities.append(amenity)
    return found_amenities

def construct_query(customer_query):
    location = extract_location(customer_query)
    price_range = extract_price_range(customer_query)
    room_type = extract_room_type(customer_query)
    amenities = extract_amenities(customer_query)

    expression = "1 = 1"
    expression_values = {}

    if location:
        expression += " AND Location = :location"
        expression_values[':location'] = location
    
    if price_range:
        expression += " AND Price BETWEEN :min_price AND :max_price"
        expression_values[':min_price'] = price_range[0]
        expression_values[':max_price'] = price_range[1]

    if room_type:
        expression += " AND RoomType = :room_type"
        expression_values[':room_type'] = room_type

    if amenities:
        for i, amenity in enumerate(amenities):
            expression += f" AND Amenities CONTAINS :amenity{i}"
            expression_values[f':amenity{i}'] = amenity

    return expression, expression_values