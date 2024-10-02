def dms_to_dd(coord_pair):
    """Converts a pair from Degrees Minute Seconds to Decimal Degrees """
    # ("26.02333333N", 097.12833333W") >>  (26.02333333, -97.12833333)
    #FAA coordinates in XML are technically DMS but only NESW part no minutes or seconds, not really a known standard for coordinates 
    directions = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new_pair = []
    for coord in coord_pair:
        new_pair.append(float(coord.strip("WNSE")) * directions[coord[-1]])
    return new_pair