class Package:
    def __init__(self,
                 package_id='',
                 address='',
                 city='',
                 state='',
                 zipcode='',
                 delivery_time='',
                 weight='',
                 status='',
                 notes=''):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.delivery_time = delivery_time
        self.weight = weight
        self.status = status
        self.notes = notes
        self.truck_id = None
        self.departure_time = None

    def __repr__(self):
        return "Package Info - ID: {0}, " \
               "TRUCK: {1}, " \
               "ADDRESS: {2}, " \
               "CITY: {3}, " \
               "STATE: {4}, " \
               "ZIP: {5}, " \
               "DELIVERY TIME: {6}, " \
               "WEIGHT: {7}, " \
               "STATUS: {8}, " \
               "NOTES: {9}".format(self.package_id,
                                   self.truck_id,
                                   self.address,
                                   self.city,
                                   self.state,
                                   self.zipcode,
                                   self.delivery_time,
                                   self.weight,
                                   self.status,
                                   self.notes)
