CVM
POP SR1 # SR1 = 64
LS SR2 SR0 3 # SR2 = 64
BEQ SR1 SR2 2
ERROR # Verify CVM, POP, LS, BEQ. If right, continue; otherwise, error.
###################### verify vector length register operations ######################
MTCL SR1
MFCL SR3
BEQ SR3 SR2 2
ERROR # Verify MTCL, MFCL. If right, continue; otherwise, error.
###################### verify memory access operations ######################
LS SR2 SR0 4 # SR2 = 2048
LV VR1 SR1 # SR1 = 64
SV VR1 SR2
LV VR2 SR2
SEQVV VR1 VR2
POP SR3
BEQ SR3 SR1 2
ERROR # Verify LV, SV, SEQVV. If right, continue; otherwise, error.
LS SR3 SR0 2 # SR3 = 2
LVWS VR1 SR1 SR3
SVWS VR1 SR2 SR3
LVWS VR2 SR2 SR3
SEQVV VR1 VR2
POP SR3
BEQ SR3 SR1 2
ERROR # Verify LVWS, SVWS. If right, continue; otherwise, error.
LV VR2 SR0
LVI VR1 SR1 VR2
SVI VR1 SR2 VR2
LVI VR3 SR2 VR2
SEQVV VR1 VR3
POP SR3
BEQ SR3 SR1 2
ERROR # Verify LVI, SVI. If right, continue; otherwise, error.
LS SR3 SR0 5
SS SR3 SR0 64
LS SR4 SR0 64
BEQ SR3 SR4 2
ERROR # Verify SS. If right, continue; otherwise, error.
###################### verify vector operations ######################
LV VR1 SR1
ADD SR2 SR1 SR1
LV VR2 SR2
ADDVV VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify ADDVV. If right, continue; otherwise, error.
SUBVV VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify SUBVV. If right, continue; otherwise, error.
LS SR4 SR0 5
ADDVS VR3 VR1 SR4
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify ADDVS. If right, continue; otherwise, error.
SUBVS VR3 VR1 SR4
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify SUBVS. If right, continue; otherwise, error.
MULVV VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify MULVV. If right, continue; otherwise, error.
DIVVV VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify DIVVV. If right, continue; otherwise, error.
MULVS VR3 VR1 SR4
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify MULVS. If right, continue; otherwise, error.
DIVVS VR3 VR1 SR4
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify DIVVS. If right, continue; otherwise, error.
###################### verify register-register shuffle ######################
UNPACKLO VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify UNPACKLO. If right, continue; otherwise, error.
UNPACKHI VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify UNPACKHI. If right, continue; otherwise, error.
PACKLO VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify PACKLO. If right, continue; otherwise, error.
PACKHI VR3 VR1 VR2
ADD SR2 SR2 SR1
LV VR4 SR2
SEQVV VR3 VR4
POP SR3
BEQ SR3 SR1 2
ERROR # Verify PACKHI. If right, continue; otherwise, error.
###################### verify vector mask register operations ######################
# CVM and POP are verified in the beginning, So only need to verify the rest: S_VV and S_VS
SEQVV VR1 VR2
POP SR3
LS SR4 SR0 7
BEQ SR3 SR4 2
ERROR # Verify SEQVV. If right, continue; otherwise, error.
SNEVV VR1 VR2
POP SR3
LS SR4 SR0 8
BEQ SR3 SR4 2
ERROR # Verify SNEVV. If right, continue; otherwise, error.
SGTVV VR1 VR2
POP SR3
LS SR4 SR0 9
BEQ SR3 SR4 2
ERROR # Verify SGTVV. If right, continue; otherwise, error.
SLTVV VR1 VR2
POP SR3
LS SR4 SR0 10
BEQ SR3 SR4 2
ERROR # Verify SLTVV. If right, continue; otherwise, error.
SGEVV VR1 VR2
POP SR3
LS SR4 SR0 11
BEQ SR3 SR4 2
ERROR # Verify SGEVV. If right, continue; otherwise, error.
SLEVV VR1 VR2
POP SR3
LS SR4 SR0 12
BEQ SR3 SR4 2
ERROR # Verify SLEVV. If right, continue; otherwise, error.
LS SR2 SR0 5
SEQVS VR1 SR2
POP SR3
LS SR4 SR0 13
BEQ SR3 SR4 2
ERROR # Verify SEQVS. If right, continue; otherwise, error.
SNEVS VR1 SR2
POP SR3
LS SR4 SR0 14
BEQ SR3 SR4 2
ERROR # Verify SNEVS. If right, continue; otherwise, error.
SGTVS VR1 SR2
POP SR3
LS SR4 SR0 15
BEQ SR3 SR4 2
ERROR # Verify SGTVS. If right, continue; otherwise, error.
SLTVS VR1 SR2
POP SR3
LS SR4 SR0 16
BEQ SR3 SR4 2
ERROR # Verify SLTVS. If right, continue; otherwise, error.
SGEVS VR1 SR2
POP SR3
LS SR4 SR0 17
BEQ SR3 SR4 2
ERROR # Verify SGEVS. If right, continue; otherwise, error.
SLEVS VR1 SR2
POP SR3
LS SR4 SR0 18
BEQ SR3 SR4 2
ERROR # Verify SLEVS. If right, continue; otherwise, error.
###################### verify scalar operations ######################
LS SR2 SR0 5
LS SR3 SR0 6
ADD SR4 SR2 SR3
LS SR5 SR0 19
BEQ SR4 SR5 2
ERROR # Verify ADD. If right, continue; otherwise, error.
SUB SR4 SR2 SR3
LS SR5 SR0 20
BEQ SR4 SR5 2
ERROR # Verify SUB. If right, continue; otherwise, error.
AND SR4 SR2 SR3
LS SR5 SR0 21
BEQ SR4 SR5 2
ERROR # Verify AND. If right, continue; otherwise, error.
OR SR4 SR2 SR3
LS SR5 SR0 22
BEQ SR4 SR5 2
ERROR # Verify OR. If right, continue; otherwise, error.
XOR SR4 SR2 SR3
LS SR5 SR0 23
BEQ SR4 SR5 2
ERROR # Verify XOR. If right, continue; otherwise, error.
LS SR3 SR0 1
SLL SR4 SR2 SR3
LS SR5 SR0 24
BEQ SR4 SR5 2
ERROR # Verify SLL. If right, continue; otherwise, error.
SRL SR4 SR2 SR3
LS SR5 SR0 25
BEQ SR4 SR5 2
ERROR # Verify SRL. If right, continue; otherwise, error.
SRA SR4 SR2 SR3
LS SR5 SR0 26
BEQ SR4 SR5 6
ERROR # Verify SRA. If right, continue; otherwise, error.
# BEQ is verified in the beginning, So only need to verify the rest.
ERROR # Verify BNE. If right, continue; otherwise, error.
ERROR # Verify BGT. If right, continue; otherwise, error.
ERROR # Verify BLT. If right, continue; otherwise, error.
BNE SR4 SR5 -3
BGT SR4 SR5 -3
BLT SR4 SR5 -3
BGE SR4 SR5 2
ERROR # Verify BGE. If right, continue; otherwise, error.
BLE SR4 SR5 2
ERROR # Verify BLE. If right, continue; otherwise, error.
HALT # verify HALT
