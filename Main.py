# Student ID: 010877719
# Main.py
# WGUPS Routing Program

import os
import shipment_workflow
import datetime
from package_data import Package
from data_extractor import File
from distance_data import Distance

# Set file paths for packages and distance data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
parcel_record = os.path.join(DATA_DIR, 'WGUPS_Package_File.csv')
Distance_database = os.path.join(DATA_DIR, 'WGUPS_Distance_Table.csv')

#loading package data to Hash table
def import_pkg_data():
    if not os.path.exists(parcel_record):
        exit(f'Package File Could Not Be Located: {parcel_record}')
    return File(parcel_record).parse_package_data()

#loading distance data to hash table
def load_distance_table():
    if not os.path.exists(Distance_database):
        exit(f'Distance File Could Not Be Found: {Distance_database}')
    raw = File(Distance_database).parse_distance_data()
    return Distance(raw).clean_and_sort_data()

# Main menu and handles user inputs
def menu_display(package_lookup_table, distance_info):
    while True:
        print(' 1 - Add A NEW Package')
        print(' 2 - Look Up Package ID')
        print(' 3 - Display ALL Package Information And The Timestamp Time')
        print(' 4 - Display All Package Details')
        print(' 5 - Display Package Details Based On A Specific Time')
        print(' 6 - View Total Mileage Summary For All Trucks')
        print(' 7 - Exit')
        print(' 8 - Back to Menu')

#user input command
        user_entry = input('\n Please Enter A Command Here (Type a # 1-8) :\n')

# Exiting the database
        if user_entry == '7':
            print('You Are Exiting The WGUPS Database')
            break

 # go back to main menu
        elif user_entry in {'8', 'Back to Main Menu'}:
            continue

        # look up package using the ID #
        elif user_entry == '1':
            try:
                print("\nPlease Enter The Following Package Details:\n")
                pkg_id = int(input('Package ID: '))
                p = Package(
                    str(pkg_id),
                    input('Shipping Location: '),
                    input('City: '),
                    input('State: '),
                    input('Zip code: '),
                    input('Target Arrival Date (Example, 12:30 PM): '),
                    input('Package Weight (LBS): '),
                    input('Status: '),
                    input('Important Notes: ')
                )
                if package_lookup_table.add(pkg_id, p):
                    print('\nPackage Has Been Successfully Added:\n', p)
                else:
                    print('\nPackage Creation Unsuccessful—ID may be taken.')
            except ValueError:
                print('\nPackage Creation Unsuccessful—ID Must Be An Integer.')

    # Looking up the package ID
        elif user_entry == '2':
            try:
                pkg_id = int(input('\nEnter a Package ID: '))
                pkg = package_lookup_table.get(pkg_id)
                print('\nPackage details:\n', pkg if pkg else 'Cannot Locate Package')
            except ValueError:
                print('ID Must Be An Integer.')

    # Showing the current status of all packages
        elif user_entry == '3':
            for pkg in package_lookup_table.list:
                if pkg and pkg[1]:
                    s = pkg[1].status
                    print("ID:", pkg[1].package_id, "Truck:", pkg[1].truck_id, "Status:", s)


     # user gets to input a time range to view specific packages that were delivered at the time
        elif user_entry == '4':
            print('\nAll Package Details:\n')
            for pkg in package_lookup_table.list:
                if pkg and pkg[1]:
                    print(pkg[1])
                    if hasattr(pkg[1], "delivery_time") and isinstance(pkg[1].delivery_time, datetime.datetime):
                        print("Delivered at:", pkg[1].delivery_time.strftime("%I:%M:%S %p"))
                    else:
                        print("Delivered at: N/A")



 # Allows user to input time range to see when packages were delivered
        elif user_entry == '5':
            try:
                start_str = input("Enter start time (e.g., 10:00 AM): ").strip()
                end_str = input("Enter end time (e.g., 12:00 PM): ").strip()
                base_date = datetime.date(2024, 1, 1)
                start_input = datetime.datetime.strptime(start_str, "%I:%M %p").time()
                end_input = datetime.datetime.strptime(end_str, "%I:%M %p").time()
                start_time = datetime.datetime.combine(base_date, start_input)
                end_time = datetime.datetime.combine(base_date, end_input)
                found = False
                print(f"\nPackages delivered between {start_str} and {end_str}:\n")
                for pkg in package_lookup_table.list:
                    if pkg and pkg[1]:
                        p = pkg[1]

                        if hasattr(p, "delivery_time") and isinstance(p.delivery_time, datetime.datetime):
                            if start_time <= p.delivery_time <= end_time:
                                print(p)
                                found = True
                if not found:
                    print("No packages were delivered during this time window.")
            except ValueError:
                print("Invalid format. Please use HH:MM AM/PM (Example, 10:00 AM).")

# calculates and prints the total mileages for Trucks
        elif user_entry == '6':
            try:
                truck1, truck2, truck3 = shipment_workflow.deliver_packages(package_lookup_table, distance_info, 'summary')
                total_miles = truck1.miles + truck2.miles + truck3.miles
                print('\n--- Total Mileage Summary ---')
                print(f'Truck 1: {truck1.miles:.1f} miles')
                print(f'Truck 2: {truck2.miles:.1f} miles')
                print(f'Truck 3: {truck3.miles:.1f} miles')
                print(f'TOTAL: {total_miles:.1f} miles\n')
            except Exception as e:
                print("Could not retrieve mileage summary:", e)


#loads the data and launches menu
if __name__ == "__main__":
    print(' ** WGUPS DATABASE ** ')
    packages = import_pkg_data()
    distances = load_distance_table()

    # menu display
    menu_display(packages, distances)

