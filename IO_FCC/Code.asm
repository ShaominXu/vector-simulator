CVM
LS SR1 SR0 0 # SR1 = 1
LS SR2 SR0 1 # SR2 = 2
LS SR3 SR0 2 # SR3 = 64 is VF length
LS SR4 SR0 3 # SR4 = 256 is vector length
LS SR6 SR0 4 # SR6 = 256 * 258 is the pointer to store data
MTCL SR3 # Set the length of vector to 64
# Load vector a
ADD SR5 SR0 SR0
LV VR0 SR5 # SR5 is the pointer to load data
ADD SR5 SR5 SR3
LV VR2 SR5
ADD SR5 SR5 SR3
LV VR4 SR5
ADD SR5 SR5 SR3
LV VR6 SR5
# Load matrix W[j]
ADD SR5 SR5 SR3
LV VR1 SR5
ADD SR5 SR5 SR3
LV VR3 SR5
ADD SR5 SR5 SR3
LV VR5 SR5
ADD SR5 SR5 SR3
LV VR7 SR5
# Multiply vector a by matrix W[j]
MULVV VR1 VR0 VR1
MULVV VR3 VR2 VR3
MULVV VR5 VR4 VR5
MULVV VR7 VR6 VR7
# Add the results from length 256 to 64
ADDVV VR1 VR1 VR3
ADDVV VR5 VR5 VR7
ADDVV VR1 VR1 VR5
# Store the result
SVWS VR1 SR6 SR4
ADD SR6 SR6 SR1
ADD SR7 SR7 SR1 # SR7 = j + 1
BLT SR7 SR4 -22 # If j < 256, repeat
# load vector b
LS SR6 SR0 4
SUB SR6 SR6 SR4
LV VR0 SR6
ADD SR6 SR6 SR3
LV VR1 SR6
ADD SR6 SR6 SR3
LV VR2 SR6
ADD SR6 SR6 SR3
LV VR3 SR6
ADD SR7 SR0 SR0 # SR7 = 0 is i
# load the results[i]
ADD SR6 SR6 SR3
LV VR4 SR6
ADD SR6 SR6 SR3
LV VR5 SR6
ADD SR6 SR6 SR3
LV VR6 SR6
ADD SR6 SR6 SR3
LV VR7 SR6
# Add the results (a * W) and vector b
ADDVV VR0 VR0 VR4
ADDVV VR1 VR1 VR5
ADDVV VR2 VR2 VR6
ADDVV VR3 VR3 VR7
ADD SR7 SR7 SR1 # SR7 = i + 1
BLT SR7 SR3 -15 # If i < 64, repeat
# save the results to address 0
ADD SR6 SR0 SR0
SV VR0 SR6
ADD SR6 SR6 SR3
SV VR1 SR6
ADD SR6 SR6 SR3
SV VR2 SR6
ADD SR6 SR6 SR3
SV VR3 SR6
HALT