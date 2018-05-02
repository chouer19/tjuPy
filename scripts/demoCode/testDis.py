
import sys
import math
sys.path.append("../../libs")

import UTM
from proPrint import *

with open('tju.map') as f:
    line = f.readline()
    while line:
        Contents = line.split('\t')

        line = f.readline()
        if len(Contents) < 5:
            continue
        content = Contents[4].split(',')
        if len(content) < 3:
            continue
        lat = float(content[1])
        lon = float(content[0])
        e,n,z,z_l = UTM.from_latlon(lat,lon)
        
        for cont in Contents[5:]:
            if len(cont.split(',')) < 3:
                continue
            lat = float(cont.split(',')[1])
            lon = float(cont.split(',')[0])
            
            ee,nn,z,z_l = UTM.from_latlon(lat,lon)
            if (e - ee) ** 2 + (n - nn) ** 2 < 0.25:
                prRed(math.sqrt((e - ee) ** 2 + (n - nn) ** 2))
            else:
                prGreen(math.sqrt((e - ee) ** 2 + (n - nn) ** 2))

            e,n = ee,nn
