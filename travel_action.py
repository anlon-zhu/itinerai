from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Union


class TravelAction:
    '''
    Action class representing state transitions.
    '''

    def __init__(
            self, mode, from_loc, to_loc, departing_at: datetime,
            arriving_at: datetime, cost, duration=None, stops=None,
            segments: List[Union[FlightSegment]] = []) -> None:
        self.mode = mode  # flight, train, or rideshare
        self.from_loc = from_loc  # previous city location
        self.to_loc = to_loc  # new city location
        self.departing_at = departing_at
        self.arriving_at = arriving_at
        self.cost = cost
        self.duration = duration
        self.stops = stops
        self.segments = segments

    def __str__(self) -> str:
        return f"{self.mode} from {self.from_loc} to {self.to_loc} for {self.duration} ({self.departing_at} - {self.arriving_at}), costing {self.cost}"


class FlightSegment:
    '''
    Flight segment class representing a single flight.
    '''

    def __init__(
            self, origin, destination, departing_at: datetime,
            arriving_at: datetime, duration: timedelta = None,
            distance_km=0.0, aircraft=None, marketing_carrier=None,
            marketing_flight_number=None) -> None:
        self.origin = origin
        self.destination = destination
        self.departing_at = departing_at
        self.arriving_at = arriving_at
        self.duration = duration
        self.distance_km = distance_km
        self.aircraft = aircraft
        self.marketing_carrier = marketing_carrier
        self.marketing_flight_number = marketing_flight_number

    def __str__(self) -> str:
        return f"Flight {self.marketing_carrier.iata_code} {self.marketing_flight_number} from {self.origin} to {self.destination} for {self.duration}"
