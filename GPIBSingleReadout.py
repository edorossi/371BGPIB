#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyvisa
import re
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

rm = pyvisa.ResourceManager()
instlist = rm.list_resources()

for i in instlist:
	tempinst = pyvisa.ResourceManager().open_resource(i)
	if "371B" in tempinst.query('ID?'):
		inst371B = tempinst
		print("371B Found")

print(inst371B.query('DOT?'))
print(inst371B.query('REAdout?'))
inst371B.write('CUr?')
rawCurve = inst371B.read_raw()

filterCurve = rawCurve[26:len(rawCurve)-1] # Removing header and isolate the data (the last byte is just a checksum)

X = []
Y = []

# horrible decoding. The data is divided in XXYYXXYY..., so 2 bytes for an X-value followed by 2 bytes for the corresponding Y-value
for kk in range(int(len(filterCurve)/4)):
	X.append(filterCurve[4 * kk] * 256 + filterCurve[4 * kk + 1])
	Y.append(filterCurve[4 * kk + 2] * 256 + filterCurve[4 * kk + 3])

print(X)
print(Y)

print(inst371B.query('SET?'))
print(inst371B.query('WFMpre?'))