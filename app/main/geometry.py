from csv import writer
import math
import re


# Converts a GPX file into a CSV file with a list of the latitude/longitude/elevation points
def process_gpx(filename_in, filename_out):
    
    with open(filename_in) as file:
        raw = file.read()

    # Use Regex to grab all lat/lon pairs
    pattern = re.compile(r'<trkpt lat="(?P<lat>\d+.\d+)" lon="(?P<lon>\d+.\d+)">\n\s+<ele>(?P<ele>(?:-?\d+)?)</ele>')
    dat = pattern.findall(raw)

    # Convert all lat/lon pairs to x/y/z
    a = 6378.137*1000
    e2 = 0.006694380004260827
    xyz = []
    for row in dat:
        phi = math.radians(float(row[0]))
        lam = math.radians(float(row[1]))
        h = float(row[2])
        chi = math.sqrt(1-e2*math.sin(phi)*math.sin(phi))
        x = (a/chi + h)*math.cos(phi)*math.cos(lam)
        y = (a/chi + h)*math.cos(phi)*math.sin(lam)
        z = (a*(1-e2)/chi + h)*math.sin(phi)
        xyz.append([x,y,z])

    # Get cumulative distance
    dcum = [0]
    for i in range(1,len(xyz)):
        r1 = xyz[i]
        r0 = xyz[i-1]
        dr = [r1[0] - r0[0], r1[1] - r0[1], r1[2] - r0[2]]
        d = math.sqrt(dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2])
        dcum.append(dcum[-1]+d/1000)

    # Write the lat/lon pairs to a CSV file
    with open(filename_out, "w") as file:
        csv_writer = writer(file)
        csv_writer.writerow(['latitude','longitude','elevation','km'])
        for i in range(len(dat)):
            newrow = [float(dat[i][0]), float(dat[i][1]), float(dat[i][2]), dcum[i]]
            # print('adding row')
            # print(newrow)
            csv_writer.writerow(newrow)

    return dcum[-1]