#!/usr/bin/python3
#
# generate CORDIC phase values
#
# 07-11-2016 E. Brombaugh

import numpy as np
import math as math
from write_memh import write_memh

dsz = 16
psz = 16
iterations = 16

# constants
pscl = (2**(psz-1))-1
itr = range(iterations)
phi = [int(math.atan(2**-i)/math.pi * 2**(psz-1) + 0.5) for i in itr]
k = 1
for i in itr:
    k = k*math.sqrt(1 + 2**(-2*i))
k = int(2**dsz/k)

print(k)

write_memh("r2p_phi_lut.memh", phi)
