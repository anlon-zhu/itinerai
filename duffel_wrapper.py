from duffel_api import Duffel
from dotenv import load_dotenv
import os
import requests

load_dotenv()


class DuffelWrapper:
    def __init__(self):
        self.access_token = os.getenv('DUFFEL_ACCESS_TOKEN')
        self.client = Duffel(access_token=self.access_token)
        self.base_url = "https://api.duffel.com"

    def search_flights(self, origin, destination, departure_date):
        offer_request = self.client.offer_requests.create().passengers([{"type": "adult"}]).slices(
            [{"origin": origin, "destination": destination, "departure_date": departure_date}]).cabin_class("economy").execute()
        return offer_request

    def search_flights_partial(
            self, origin, destination, departure_date):
        partial_offer_request = self.client.partial_offer_requests.create().passengers([{"type": "adult"}]).slices(
            [{"origin": origin, "destination": destination, "departure_date": departure_date}]).cabin_class("economy").execute()
        return partial_offer_request

    def list_places(
            self, query=None, name=None, radius=None, latitude=None,
            longitude=None):
        '''
        List places by query, name, or location, limited to 20 places
        '''
        url = f"{self.base_url}/places/suggestions"
        headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "Duffel-Version": "v1",
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "query": query,
            "name": name,
            "rad": radius,
            "lat": latitude,
            "lng": longitude
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
        return response.json()


if __name__ == '__main__':
    duffel = DuffelWrapper()
    print('Search Flights')
    print(duffel.search_flights('LAX', 'JFK', '2024-12-25'))
    print('Search Flights Partial')
    print(duffel.search_flights_partial('LAX', 'JFK', '2024-12-25'))
    print('List Places by Name')
    print(duffel.list_places(name='LAX')['data'])
    print('List Places by Location')
    print(duffel.list_places(latitude=40.7128,
          longitude=-74.0060, radius=10000))
