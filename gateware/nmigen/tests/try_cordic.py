# try cordic operations

import math as math

def r2p(x, y):
    # set up constants
    iterations = 16
    itr = range(iterations)
    phi = [math.atan(2**-i) for i in itr]
    k = 1
    for i in itr:
        k = k*math.sqrt(1 + 2**(-2*i))
    
    #print(phi)
    
    #print(k)
    
    # init phase accum
    phs = 0
    
    # handle x<0
    if(x<0):
        x=-x
        y=-y
        phs = math.pi
    
    # do the iterations
    for i in itr:
        px = x
        py = y
        if(y>=0):
            y = py - px/(2**i)
            x = px + py/(2**i)
            phs = phs + phi[i]
        else:
            y = py + px/(2**i)
            x = px - py/(2**i)
            phs = phs - phi[i]
    
        print(i, x, y, phs)
    
    x = x/k
    phs = phs
    print(x, 180*phs/math.pi)