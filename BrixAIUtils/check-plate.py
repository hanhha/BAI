#!/usr/bin/env python3
from argparse import ArgumentParser as ArgParser
import VehicleCheck

ap = ArgParser()
ap.add_argument ('-p', '--plate', default = '51f-81420', help = 'Plate number')
args = ap.parse_args ()
plate = args.plate

list_of_vi = VehicleCheck.check_violation (plate)

for idx, report in enumerate(list_of_vi):
    print ('Loi %d' %(idx + 1))
    print ('Ngay vi pham: %s'  %(report['date'].encode('latin-1').decode()))
    print ('Vi tri vi pham: %s'  %(report['place'].encode('latin-1').decode()))
    print ('Loi vi pham: %s'  %(report['description'].encode('latin-1').decode()))
    print ('Co quan xu ly: %s' %(report['dept'].encode('latin-1').decode()))

