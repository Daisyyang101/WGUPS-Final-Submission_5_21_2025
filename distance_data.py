
# standardizes address
def normalize_address(address):
    address = address.upper().strip()
    address = address.replace("EAST", "E").replace("WEST", "W")
    address = address.replace("SOUTH", "S").replace("NORTH", "N")
    address = address.replace("STREET", "ST").replace("AVENUE", "AVE")
    return address

class Distance:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.distance_table = []
        self.labels = []

# cleans and formats raw CSV data into nested list
    def clean_and_sort_data(self):
        header = self.raw_data.pop(0)
        self.labels = [normalize_address(h) for h in header if h != '']

        for row in self.raw_data:
            loc = normalize_address(row[0])
            distances = []
            for i in range(1, len(row)):
                if i - 1 < len(self.labels):
                    place = self.labels[i - 1]
                    dist = row[i]
                    distances.append([place, dist])
            self.distance_table.append([loc, distances])

        return self.distance_table

    # returns the place names
    def get_labels(self):
        return self.labels
