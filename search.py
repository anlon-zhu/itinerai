from datetime import date, timedelta
from location_state import LocationState
from travel_action import TravelAction
from typing import List
from duffel_api import Duffel
import asyncio
from duffel_wrapper import DuffelWrapper


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
            flights = self.duffel.search_flights_partial(
                state.airport_iata, airport, state.date)

            for offer in flights.offers:
                total_amount = offer.total_amount
                # total_emissions_kg = offer.total_emissions_kg
                # total_currency = offer.total_currency
                # tax_currency = offer.tax_currency
                # tax_amount = offer.tax_amount
                # supported_passenger_identity_document_types = offer.supported_passenger_identity_document_types

                for slice_data in offer.slices:
                    # departure_date = slice_data.departure_date

                    for segment in slice_data.segments:
                        stops = segment.stops
                        operating_carrier_flight_number = segment.operating_carrier_flight_number
                        operating_carrier_name = segment.operating_carrier.name
                        duration = segment.duration
                        distance = segment.distance
                        # origin_name = segment.origin.name
                        # origin_city_name = segment.origin.city_name
                        # destination_name = segment.destination.name
                        # destination_city_name = segment.destination.city_name

                        # Process stops
                        for stop in stops:
                            stop_duration = stop.duration
                            departing_at = stop.departing_at
                            arriving_at = stop.arriving_at
                            stop_airport_name = stop.airport.name
                            stop_city_name = stop.airport.city_name
                            # Access more details about the stop as needed

                        # Process aircraft
                        # aircraft_name = segment.aircraft.name

                    action = TravelAction(
                        mode="flight",
                        from_loc=state.airport_iata,
                        to_loc=airport,  # potential airport
                        duration=duration,
                        cost=total_amount,
                        carrier=operating_carrier_name
                    )

                    actions.append(action)

            # Step 2: Google Maps: city A to city B via public transit or rideshare
        return actions

    def result(self, state: LocationState, action: TravelAction) -> LocationState:
        # Assuming action.duration is a timedelta object for simplicity
        new_date = state.date + action.duration
        new_cost = state.cost + action.cost
        new_stops = state.stops + 1

        # Here you might want to check if the new state exceeds budget or max stops
        if new_cost > self.budget or new_stops > self.max_stops:
            return None  # This action leads to an invalid state

        return LocationState(
            action.to_city, new_date, state.time, state.days_left -
            action.duration.days, stops=new_stops, cost=new_cost)

    def cost_fxn(self):
        # Some linear function of cost, time_spent_at_goal, distance from goal
        pass


if __name__ == "__main__":
    # Example initialization of start and goal states
    start_state = LocationState(
        airport_iata="SNA", city="Santa Ana", date="2024-05-01",
        time="10:00", days_left=10)
    goal_state = LocationState(
        airport_iata="EWR", city="Newark", date="2024-05-15",
        time="10:00", days_left=0)

    bfs = BestFirstSearch(
        start=start_state, goal=goal_state, budget=1000, max_stops=2,
        min_stay_duration=2)

    # Run the async actions method in an event loop
    actions = asyncio.run(bfs.actions(start_state))

    for action in actions:
        print(str(action) + f" via {action.carrier} for ${action.cost}")
