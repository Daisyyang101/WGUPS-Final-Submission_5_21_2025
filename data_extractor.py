import csv
import re
from hash_table import Hash
from package_data import Package

#reading and loading data from CSV file
class File:
    def __init__(self, file):
        self.file = file

    def parse_package_data(self):
        row_count = self._count_rows() - 1
        hash_table = Hash(row_count)

    # open and reads CSV file
        with open(self.file, mode='r', encoding='utf-8-sig') as csv_data:
            reader = csv.reader(csv_data)
            next(reader)
            for row in reader:
                clean_address = re.sub(r'[#,].*$', '', row[1]).strip()

                package = Package(
                    # create package object for the rows
                    package_id=row[0],
                    address=clean_address,
                    city=row[2],
                    state=row[3],
                    zipcode=row[4],
                    delivery_time=row[5],
                    weight=row[6],
                    status='At HUB', #ALL PACKAGES START AT THE HUB
                    notes=row[7]
                )

                hash_table.add(row[0], package) #aDDS PACKAGE TO THE HASH TABLE using pkg ID
        return hash_table

    def _count_rows(self):
        with open(self.file, mode='r', encoding='utf-8-sig') as f:
            return sum(1 for _ in f)

    def parse_distance_data(self):
        raw_data = []
        with open(self.file, mode='r', encoding='utf-8-sig', newline='') as csv_data:
            reader = csv.reader(csv_data)
            for row in reader:
                if row[0] == '5383 S 900 East #104':
                    row[0] = '5383 South 900 East'
                raw_data.append(row)
        return raw_data
