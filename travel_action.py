class TravelAction:
    def __init__(
            self, mode, from_loc, to_loc, duration, cost, carrier) -> None:
        self.mode = mode  # flight, train, or rideshare
        self.from_loc = from_loc  # previous city location
        self.to_loc = to_loc  # new city location
        self.duration = duration  # new start date/time, increments days left
        self.cost = cost
        self.carrier = carrier

    def __str__(self) -> str:
        return f"Travel by {self.mode} from {self.from_loc} to {self.to_loc} in {self.duration}"
