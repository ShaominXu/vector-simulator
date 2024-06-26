CVM
LS SR1 SR0 11 # SR1 = 64
MTCL SR1
# load matrix f and multiply by kernel
ADD SR3 SR0 SR0 # SR3 = 0 row pointer
ADD SR7 SR0 SR0 # SR7 = 0 result address
ADD SR6 SR0 SR0 # SR6 = 0 counter
# start loop over f rows
ADD SR4 SR0 SR0 # SR4 = 0 kernel[i]
# start loop over kernel[:]
ADD SR2 SR0 SR0 # SR2 = 0 is j
# start loop over kernel[i][:]
ADD SR5 SR3 SR2
LS SR1 SR0 10 # SR1 = 2 is stride
LVWS VR1 SR5 SR1
LS SR1 SR0 12 # SR1 = 128
ADD SR5 SR5 SR1
LS SR1 SR0 10 # SR1 = 2 is stride
LVWS VR3 SR5 SR1
ADD SR5 SR4 SR2
LS SR1 SR5 0 # SR1 = kernel[i][j]
MULVS VR1 VR1 SR1
MULVS VR3 VR3 SR1
ADDVV VR2 VR2 VR1
ADDVV VR4 VR4 VR3
LS SR1 SR0 9 # SR1 = 1
ADD SR2 SR2 SR1
LS SR1 SR0 16 # SR1 = 3
BLT SR2 SR1 -17 # loop over kernel[i][:]
ADD SR4 SR4 SR1
LS SR1 SR0 13 # SR1 = 256
ADD SR3 SR3 SR1
LS SR1 SR0 15 # SR1 = 9
BLT SR4 SR1 -24 # loop over kernel[:]
# store result
SV VR2 SR7
LS SR1 SR0 11 # SR1 = 64
ADD SR7 SR7 SR1
SV VR4 SR7
LS SR2 SR0 9 # SR2 = 1
SUB SR1 SR1 SR2 # SR1 = 63
ADD SR7 SR7 SR1
# next row of f
ADDVV VR2 VR0 VR0
ADDVV VR4 VR0 VR0
LS SR1 SR0 13 # SR1 = 256
SUB SR3 SR3 SR1
LS SR1 SR0 9 # SR1 = 1
ADD SR6 SR6 SR1
LS SR2 SR0 12 # SR1 = 128
SUB SR1 SR2 SR1
BLT SR6 SR1 -44 # loop over f rows
HALT
