CVM
LS SR1 SR0 0 # SR1 = 64
LS SR2 SR0 1 # SR2 = 450
LS SR3 SR0 2 # SR3 = 2048
LS SR4 SR0 3 # SR4 = 2
LS SR5 SR0 4 # SR5 = 1
MTCL SR4
LV VR1 SR0
ADD SR6 SR0 SR2
LV VR5 SR6
MULVV VR2 VR1 VR5
ADD SR0 SR0 SR4
ADDVV VR3 VR3 VR2
BEQ SR1 SR4 3
MTCL SR1
MFCL SR4
BLE SR0 SR2 -9
SV VR3 SR3
SRL SR1 SR1 SR5
MTCL SR1
LV VR0 SR3
ADD SR4 SR3 SR1
LV VR1 SR4
ADDVV VR3 VR1 VR0
BGT SR1 SR5 -7
SV VR3 SR3
HALT