#stores truck info

class Truck:
    def __init__(self, truck_id, departure_time):
        self.id = truck_id
        self.departure_time = departure_time
        self.truck = []
        self.speed = 18
        self.miles = 0
        self.capacity = 16
        self.status = 'At HUB'

#adds package to the trucks list
    def add_package(self, package):
        self.truck.append(package)

#removes package
    def remove_package(self, package):
        self.truck.remove(package)

#add truck mileage
    def add_miles(self, miles):
        self.miles += miles

#update trucks status
    def set_status(self, status):
        self.status = status