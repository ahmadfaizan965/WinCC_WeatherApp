from opcua import Server , ua
import time
import requests

API_KEY = "YOUR A.P.I KEY"

# Create OPC UA server
server = Server()

# Replace 0.0.0.0 as per your PC local IP Address
server.set_endpoint("opc.tcp://0.0.0.0:4092/weather/server/")
idx = server.register_namespace("WeatherApp")

# Create object and variables
objects = server.get_objects_node()
device = objects.add_object(idx, "WeatherStation")

# Create 2 Important tags i.e city_input & Search Trigger
city = device.add_variable(idx, "city_input", "")
search = device.add_variable(idx, "search_trigger", False)

# Create all the tags for data you want to fetch from API like temp, humidity, wind speed etc.
temperature = device.add_variable(idx, "temperature", 0.0)
wind_kph = device.add_variable(idx, "wind_speed", 0.0)
condition_text = device.add_variable(idx, "desc", "")

# Make writable
city.set_writable()
search.set_writable()

server.start()
print("Weather OPC UA Server started and ready...")

try:
    while True:
        if search.get_value():
            city_name = city.get_value().strip()

            # request
            url = f"http://api.weatherapi.com/v1/current.json"
            params = {
                "key": API_KEY,
                "q": city_name,
                "aqi": "no"
            }

            print(f"Requesting weather for: {city_name}")
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Parse values
                temp = data["current"]["temp_c"]
                w_kph = data["current"]["wind_kph"]
                cond = data["current"]["condition"]["text"]

                # Update OPC UA variables
                temperature.set_value(temp)
                wind_kph.set_value(w_kph)
                condition_text.set_value(cond)

                #Update OPC UA Tags to display API data in WinCC Screen
                temperature.set_value(ua.Variant(float(temp)))
                wind_kph.set_value(ua.Variant(float(w_kph)))
                condition_text.set_value(ua.Variant(str(cond)))

                print("Weather updated:", city_name)

            else:
                print("Error from WeatherAPI:", response.status_code)

            # Reset trigger
            search.set_value(False)

        time.sleep(0.2)

except KeyboardInterrupt:
    pass

finally:
    server.stop()
    print("Server stopped.")
