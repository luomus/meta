# Script to convert sliding YKJ coordinates (liukukoordinaatit) to ISO 6709

def pad(s):
    return s + '0' * (7 - len(s))

def increment_end(coordinate_str, slice_str):
    result = coordinate_str[:-len(slice_str)] + slice_str
    result_int = int(result) + 1
    return str(result_int)

def sliding_to_iso6709(ykj):
    ykj = str(ykj).replace(" ", "")
    try:
        ykj_parts = ykj.split(":")

        # Northing
        if "-" in ykj_parts[0]:
            n_parts = ykj_parts[0].split("-")
            n = n_parts[0]
            n_slide = n_parts[1]

            n_min = pad(n)
            n_max = pad(increment_end(n, n_slide))
        else:
            n = ykj_parts[0]
            n_min = pad(ykj_parts[0])
            n_max = pad(str(int(n) + 1))

        # Easting
        ykj_parts[1] = "3" + ykj_parts[1]

        if "-" in ykj_parts[1]:
            e_parts = ykj_parts[1].split("-")
            e = e_parts[0]
            e_slide = e_parts[1]

            e_min = pad(e)
            e_max = pad(increment_end(e, e_slide))
        else:
            e = ykj_parts[1]
            e_min = pad(ykj_parts[1])
            e_max = pad(str(int(e) + 1))

        # ISO 6709 format example:
        # /6698900:3186200/6699400:3186200/6699400:3186600/6698900:3186600/6698900:3186200/
        # CRSEPSG:2393

        #              1               2               3               4               5                                      
        iso_format = f"/{n_min}:{e_min}/{n_max}:{e_min}/{n_max}:{e_max}/{n_min}:{e_max}/{n_min}:{e_min}/\nCRSEPSG:2393"

        return iso_format
    except ValueError as e:
        print(f"Error processing coordinates: {ykj}")
        raise

# Test coordinates without first 3 of easting
"""
ykj = "6661:158-9" # Kökar
ykj = "66838-46:2302-6" # Sandö
ykj = "68530-4:4309-10" # Hakulinniemi
ykj = "66878-9:3170-2" # Pipola
ykj = "6759-60:243" # Iso-Valanen
ykj = "66989-93:1862-5" # Sundholm
"""
print(sliding_to_iso6709("6661:158-9"))
