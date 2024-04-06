from datetime import date, timedelta, datetime
from location_state import LocationState
from travel_action import FlightSegment, TravelAction
from typing import List
from duffel_api import Duffel
import asyncio
from duffel_wrapper import DuffelWrapper
from isodate import parse_duration


class BestFirstSearch:
    def __init__(
            self, start: LocationState, goal: LocationState, budget,
            max_stops, min_stay_duration) -> None:
        self.start = start
        self.goal = goal
        self.budget = budget
        self.max_stops = max_stops
        self.min_stay_duration = min_stay_duration
        self.duffel = DuffelWrapper()
        # You might need more initialization here

    async def actions(self, state: LocationState) -> List[TravelAction]:
        actions = []

        # Step 0: Generate all possible next airports
        next_airports = state._get_next_airports(self.goal)

        for airport in next_airports:
            # Step 1. Duffel: partial offer requests for (multi-city) flights from current city to another city
            # TODO: try a number of days window
            response = self.duffel.search_flights_partial(
                state.airport_iata, airport, state.datetime)

            for offer in response.offers:
                if len(offer.slices) == 0:
                    raise ValueError("No slices found in offer")

                # We request 1 slice (point A to point B), so this always returns 1 slice
                slice = offer.slices[0]

                action_departing_at = None
                action_arriving_at = None
                action_duration = timedelta(0)
                action_cost = offer.total_amount
                action_stops = 0
                action_segments = []

                # May have multiple segments/stops in an offer
                for i, segment in enumerate(slice.segments):
                    # Times
                    departing_at = segment.departing_at
                    arriving_at = segment.arriving_at
                    # Locations
                    origin_airport = segment.origin.iata_code
                    destination_airport = segment.destination.iata_code

                    # Identification
                    aircraft = segment.aircraft
                    marketing_carrier = segment.marketing_carrier
                    marketing_flight_number = segment.marketing_carrier_flight_number

                    # nullable attributes
                    duration = parse_duration(
                        segment.duration
                        if segment.duration is not None else 'PT0S')
                    distance_km = float(
                        segment.distance) if segment.distance is not None else 0.0

                    if i == 0:
                        if origin_airport != state.airport_iata:
                            raise ValueError(
                                f"Origin airport {origin_airport} does not match current state {state.airport_iata}")
                        action_departing_at = departing_at

                    if i == len(slice.segments) - 1:
                        if destination_airport != airport:
                            raise ValueError(
                                f"Destination airport {destination_airport} does not match goal {airport}")
                        action_arriving_at = arriving_at

                    cleaned_segment = FlightSegment(
                        origin=origin_airport,
                        destination=destination_airport,
                        departing_at=departing_at,
                        arriving_at=arriving_at, duration=duration,
                        distance_km=distance_km, aircraft=aircraft,
                        marketing_carrier=marketing_carrier,
                        marketing_flight_number=marketing_flight_number)

                    action_segments.append(cleaned_segment)
                    action_stops += len(segment.stops)
                    action_duration += duration
                    # TODO: Differentiate between flight transfers and stops

                action = TravelAction(
                    mode="flight", from_loc=state.airport_iata,
                    to_loc=airport, departing_at=action_departing_at,
                    arriving_at=action_arriving_at, cost=action_cost,
                    duration=action_duration, stops=action_stops,
                    segments=action_segments)
                actions.append(action)

            # Step 2: Google Maps: city A to city B via public transit or rideshare
        return actions

    def result(self, state: LocationState, action: TravelAction) -> LocationState:
        new_date = state.datetime + action.duration
        new_cost = state.cost + action.cost
        new_stops = state.stops + 1

        if new_cost > self.budget or new_stops > self.max_stops:
            return None  # This action leads to an invalid state

        # TODO: edit number of stops and days left logic
        return LocationState(
            airport_iata=action.to_loc, city=action.to_loc,
            datetime=new_date, days_left=state.days_left - 1,
            stops=new_stops, cost=new_cost)

    def cost_fxn(self):
        # Some linear function of cost, time_spent_at_goal, distance from goal
        pass


if __name__ == "__main__":
    # Example initialization of start and goal states
    start_state = LocationState(
        airport_iata="SNA", city="Santa Ana", datetime=datetime.now(),
        days_left=5)
    goal_state = LocationState(
        airport_iata="EWR", city="New Jersey", datetime=datetime.now(),
        days_left=5)

    bfs = BestFirstSearch(
        start=start_state, goal=goal_state, budget=1000, max_stops=2,
        min_stay_duration=2)

    # Run the async actions method in an event loop
    actions = asyncio.run(bfs.actions(start_state))

    actions.sort(key=lambda x: x.cost)
    for action in actions:
        print(str(action))
        if action.to_loc == goal_state.airport_iata:
            print("Goal reached!")
            for segment in action.segments:
                print(segment)
