# Shipment workflow - loads 40 packages onto the 3 trucks and finds the best delivery routes using nearest neighbor approach and 2-opt optimzation.

from truck_data import Truck
from distance_data import normalize_address
import datetime

# Determines the expected delivery time of a package based on distance and time.
def tick(mileage, time):
    return time + datetime.timedelta(seconds=(mileage / 18) * 3600)

# Assigns a package to a truck with notes handling
def truck_allocation(pkg, truck, raw_entry, addresses_to_visit, label, pkg_data):
    notes = pkg.notes.lower()

# Do not assign to wrong truck
    if 'can only be on truck 2' in notes and truck.id != 2:
        return

# Handle delayed packages
    if 'delayed' in notes:
        delay_time = datetime.datetime.strptime('09:05 AM', '%I:%M %p').time()
        if truck.departure_time.time() < delay_time:
            return

# Handle wrong address fix
    if 'wrong address listed' in notes:
        fix_time = datetime.datetime.strptime('10:20 AM', '%I:%M %p').time()
        if truck.departure_time.time() >= fix_time:
            pkg.address = '410 S State St'

# Assign package to truck
    if not hasattr(truck, 'packages'):
        truck.packages = []
    truck.packages.append(pkg)
    pkg.status = label
    pkg.truck_id = truck.id
    pkg.departure_time = truck.departure_time
    normalized_addr = normalize_address(pkg.address)
    if normalized_addr not in addresses_to_visit:
        addresses_to_visit.append(normalized_addr)

    raw_entry[0] = int(raw_entry[0])
    raw_entry[1] = pkg
    pkg_data.add(raw_entry[0], raw_entry[1])

# Builds truck groups based on "Must be delivered with" note
def build_truck_groups(pkg_data):
    grouped = {}
    visited = set()

    for pkg_id in range(1, 41):
        pkg = pkg_data.get(pkg_id)
        if not pkg or pkg_id in visited:
            continue

        notes = pkg.notes.lower()
        if 'must be delivered with' in notes:
            try:
                parts = notes.split('with')[-1].strip()
                related_ids = [int(x) for x in parts.replace(',', '').split()]
                all_ids = list(set(related_ids + [pkg_id]))

                for pid in all_ids:
                    grouped[pid] = all_ids
                    visited.add(pid)
            except:
                continue

    return grouped

# Loads list of pkg Ids to the truck and returns delivery address
def truck_load_up(truck, pkg_data, pkg_ids, truck_num):
    if not hasattr(truck, 'packages'):
        truck.packages = []
    addresses = []
    for package_id in pkg_ids:
        if len(truck.packages) >= 16:
            break  # Respect truck capacity
        pkg = pkg_data.get(package_id)
        if pkg:
            raw_entry = [package_id, pkg]
            truck_allocation(pkg, truck, raw_entry, addresses, f'ON TRUCK {truck_num}', pkg_data)
    return addresses

# Swaps route segments for 2-opt optimization
def two_opt_swap(route, i, k):
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

# Optimizes delivery route
def optimize(route, distance_data):
    route = ['HUB'] + route[:] + ['HUB']
    index = 2 if normalize_address('4580 S 2300 E') in route else 1
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(index, len(route) - 1):
            for k in range(i + 1, len(route)):
                new_route = two_opt_swap(best, i, k)
                if cost(new_route, distance_data)[0] < cost(best, distance_data)[0]:
                    best = new_route
                    improved = True
        route = best
    return best

# Calculates route cost and updates delivery times/statuses
def cost(route, data, time=-1, pkgs=None, check_time=0, package=None, search=False):
    total_miles = 0
    route = [normalize_address(r) for r in route]
    start = route[0]
    visited = [start]
    count = 0
    while len(visited) < len(route):
        found = False
        for row in data:
            if normalize_address(row[0]) == start:
                for dest, dist in row[1]:
                    if normalize_address(dest) == route[count + 1]:
                        miles = float(dist)
                        total_miles += miles
                        visited.insert(0, dest)
                        if time != -1:
                            time = tick(miles, time)
                        if check_time and time >= check_time:
                            if search:
                                return find_pkg_status(package, check_time, pkgs)
                            return True
                        if pkgs:
                            pkg_status_update(dest, pkgs, time)
                        start = route[count + 1]
                        count += 1
                        found = True
                        break
                break
        if not found:
            break
    if check_time:
        return find_pkg_status(package, check_time, pkgs) if search else False
    return [total_miles, time]

# Updates status and delivery time of a package
def pkg_status_update(address, pkgs, time):
    for pkg in pkgs:
        if pkg is not None and pkg[1] is not None:
            if normalize_address(pkg[1].address) == normalize_address(address):
                pkg[1].status = 'Delivered at ' + time.strftime("%H:%M:%S")
                pkg[1].delivery_time = time

# Prints status of a package at a specific time
def find_pkg_status(package, check_time, pkgs):
    for pkg in pkgs:
        if pkg[1].package_id == package.package_id:
            print('\nAt', check_time.time(), '\n\n', package)
            return True
    return False

# Main delivery simulation function
def deliver_packages(pkg_data, distance_data, status='normal', hour=None, minute=None):
    all_pkg_ids = list(range(1, 41))
    groups = build_truck_groups(pkg_data)

    # "Can only be on truck 2" filter
    t2_only = [pkg_id for pkg_id in all_pkg_ids if 'can only be on truck 2' in pkg_data.get(pkg_id).notes.lower()]
    all_ids = set(all_pkg_ids) - set(t2_only)

    t1_first = groups.get(1, [1])
    t2_first = groups.get(3, [3]) + t2_only
    t3_first = groups.get(25, [25])

    assigned_ids = set(t1_first + t2_first + t3_first)
    leftover_ids = list(all_ids - assigned_ids)

    # groups of 16
    batches = [leftover_ids[i:i + 16] for i in range(0, len(leftover_ids), 16)]

    truck1 = Truck(1, datetime.datetime(2024, 1, 1, 8, 0, 0))
    truck2 = Truck(2, datetime.datetime(2024, 1, 1, 8, 0, 0))
    truck3 = Truck(3, datetime.datetime(2024, 1, 1, 9, 5, 0))

    t1_addresses = truck_load_up(truck1, pkg_data, t1_first, 1)
    t2_addresses = truck_load_up(truck2, pkg_data, t2_first, 2)
    t3_addresses = truck_load_up(truck3, pkg_data, t3_first, 3)

    # If neededd reload truck 1
    for i, batch in enumerate(batches):
        if i == 0:
            continue
        last_time = truck1.departure_time
        if t1_addresses:
            _, last_time = cost(optimize(t1_addresses, distance_data), distance_data, last_time)
        truck1.departure_time = last_time
        t1_addresses += truck_load_up(truck1, pkg_data, batch, 1)

    # Try again with unassigned packages
    handled_ids = set()
    for pkg in pkg_data.list:
        if not pkg or pkg[1].package_id in handled_ids:
            continue

        group = groups.get(pkg[1].package_id, [pkg[1].package_id])
        if any(pkg_data.get(pid).truck_id is not None for pid in group):
            continue  # Skip if already assigned

        group_objs = [pkg_data.get(pid) for pid in group]
        raw_entries = [[obj.package_id, obj] for obj in group_objs]

        def try_truck(truck, label, addr_list):
            if len(truck.packages) + len(group_objs) <= 16:
                for raw_entry in raw_entries:
                    truck_allocation(raw_entry[1], truck, raw_entry, addr_list, label, pkg_data)
                return True
            return False

        if try_truck(truck1, 'ON TRUCK 1', t1_addresses):
            handled_ids.update(group)
        elif try_truck(truck2, 'ON TRUCK 2', t2_addresses):
            handled_ids.update(group)
        elif try_truck(truck3, 'ON TRUCK 3', t3_addresses):
            handled_ids.update(group)

    # Loads delayed packages to truck 3
    for pkg in pkg_data.list:
        if pkg and pkg[1].truck_id is None and 'delayed' in pkg[1].notes.lower():
            raw_entry = [pkg[1].package_id, pkg[1]]
            truck_allocation(pkg[1], truck3, raw_entry, t3_addresses, 'ON TRUCK 3', pkg_data)

    try:
        t1_route = optimize(t1_addresses, distance_data)
        t1_miles, _ = cost(t1_route, distance_data, truck1.departure_time, pkg_data.list)

        t2_route = optimize(t2_addresses, distance_data)
        t2_miles, _ = cost(t2_route, distance_data, truck2.departure_time, pkg_data.list)

        t3_route = optimize(t3_addresses, distance_data)
        t3_miles, _ = cost(t3_route, distance_data, truck3.departure_time, pkg_data.list)

        if status == 'normal':
            total_miles = round(t1_miles + t2_miles + t3_miles, 2)
            print("\n--- Total Mileage Summary ---")
            print(f"Truck 1: {round(t1_miles, 2)} miles")
            print(f"Truck 2: {round(t2_miles, 2)} miles")
            print(f"Truck 3: {round(t3_miles, 2)} miles")
            print(f"TOTAL: {total_miles} miles\n")

        if status == 'summary':
            truck1.miles = round(t1_miles, 2)
            truck2.miles = round(t2_miles, 2)
            truck3.miles = round(t3_miles, 2)
            return truck1, truck2, truck3

    except Exception as e:
        print("[ERROR]", e)

   
    for pkg in pkg_data.list:
        if pkg and pkg[1].truck_id is None:
            print(f"Package ID {pkg[1].package_id} is NOT assigned to any truck.")