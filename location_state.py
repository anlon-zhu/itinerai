from __future__ import annotations
from typing import List
from duffel_wrapper import DuffelWrapper
import math
from datetime import datetime

EARTH_RADIUS_KM = 6371.0


class LocationState:
    '''
    State class representing location, time, and various budgets.
    '''

    def __init__(self, airport_iata, city, datetime: datetime,
                 days_left, stops=0, cost=0, latitude=None,
                 longitude=None) -> None:
        self.airport_iata = airport_iata
        self.city = city
        self.datetime = datetime
        self.days_left = days_left
        self.stops = stops
        self.cost = cost
        self.latitude = latitude
        self.longitude = longitude
        self.duffel = DuffelWrapper()

    def __str__(self) -> str:
        return f"Airport: {self.airport_iata}, {self.city} \n DateTime: {self.datetime}"

    def _get_next_airports(
            self, goal_airport: LocationState) -> List[str]:
        '''
        Get intermediary airports in a circle bounded by two airports
        '''
        # Get the current airport's lat/lon if not provided
        if self.latitude and self.longitude:
            current_airport_lat = self.latitude
            current_airport_lon = self.longitude
        else:
            tmp = self.duffel.list_places(
                name=self.airport_iata)['data']
            tmp = [c for c in tmp if c['type'] == 'airport']
            if not tmp:
                raise ValueError(
                    f"Airport {self.airport_iata} not found")
            tmp = tmp[0]
            current_airport_lat = tmp['latitude']
            current_airport_lon = tmp['longitude']
            self.latitude = current_airport_lat
            self.longitude = current_airport_lon

        # Get the goal airport's information
        if goal_airport.latitude and goal_airport.longitude:
            goal_airport_lat = goal_airport.latitude
            goal_airport_lon = goal_airport.longitude
        else:
            tmp = self.duffel.list_places(
                name=goal_airport.airport_iata)['data']
            tmp = [c for c in tmp if c['type'] == 'airport']
            if not tmp:
                raise ValueError(
                    f"Airport {self.airport_iata} not found")
            tmp = tmp[0]
            goal_airport_lat = tmp['latitude']
            goal_airport_lon = tmp['longitude']
            goal_airport.latitude = goal_airport_lat
            goal_airport.longitude = goal_airport_lon

        # Calculate the distance between the current and goal airports
        distance = self._distance_between_points(
            current_airport_lat, current_airport_lon,
            goal_airport_lat, goal_airport_lon)

        # Set the radius to half of the distance
        radius = int(distance * 1000)
        # Calculate midpoint between current and goal airports
        midpoint_lat, midpoint_lng = (
            current_airport_lat + goal_airport_lat) / 2, (
            current_airport_lon + goal_airport_lon) / 2

        # Search for airports within the circular area
        search_response = self.duffel.list_places(
            radius=str(radius),
            latitude=str(midpoint_lat),
            longitude=str(midpoint_lng))

        next_airports = set()

        for place in search_response['data']:
            if place['type'] == 'airport':
                next_airports.add(place['iata_code'])

        # Always include the goal and never include the current airport
        next_airports.add(goal_airport.airport_iata)
        if self.airport_iata in next_airports:
            next_airports.remove(self.airport_iata)

        return list(next_airports)

    def _distance_between_points(self, lat1, lon1, lat2, lon2) -> float:
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Calculate the angular distance between the two points using the haversine formula
        angular_distance = math.acos(
            math.sin(lat1_rad) * math.sin(lat2_rad) + math.cos(lat1_rad) *
            math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad))

        # Calculate the distance between the two points using the angular distance and the Earth's radius
        distance_km = angular_distance * EARTH_RADIUS_KM

        return distance_km


if __name__ == '__main__':
    print('List Places Between Cities')
    state = LocationState(
        'LAX', 'Los Angeles', datetime=datetime.now(),
        days_left=0)
    goal = LocationState(
        'JFK', 'New York', datetime=datetime.now(),
        days_left=0)
    print(state._get_next_airports(goal))
