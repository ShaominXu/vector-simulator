# real part of input x is stored in VDMEM 0~127
# imaginary part of input x is stored in VDMEM 128~255
# real part of weights w is stored in VDMEM 256~319
# imaginary part of weights w is stored in VDMEM 320~383
# 64 2-point FFTs
LS SR4 SR0 1 # SR4 = 384
LS SR7 SR0 2 # SR7 = 1
LS SR3 SR0 3 # SR3 = 448
LS SR1 SR0 0 # SR1 = 256
# load w^0_128
LV VR0 SR1
SV VR0 SR4 # save [w^0_128 real part] *64 in VDMEM 384~447 and [w^0_128 imaginary part] *64 in VDMEM 448~511
ADD SR4 SR4 SR7
BLT SR4 SR3 -2
LS SR1 SR0 5 # SR1 = 320
LS SR3 SR0 4 # SR3 = 512
BLT SR4 SR3 -7
# load w^0_128 real part
LS SR4 SR0 1 # SR4 = 384
LV VR0 SR4
# load w^0_128 imaginary part
LS SR3 SR0 3 # SR3 = 448
LV VR1 SR3
# y_odd = fft(x[i + 64], 1) = x[i + 64] for i = 0~63
# load y_odd real part
LS SR1 SR0 6 # SR1 = 64
LV VR2 SR1
# load y_odd imaginary part
LS SR1 SR0 7 # SR1 = 192
LV VR3 SR1
# W^0_128 * y_odd[0]
LS SR1 SR0 9 # SR1 = 1000
MULVV VR4 VR0 VR2
DIVVS VR4 VR4 SR1
MULVV VR5 VR1 VR3
DIVVS VR5 VR5 SR1
SUBVV VR6 VR4 VR5 # VR6 = W^0_128 * y_odd[0] real part
MULVV VR4 VR0 VR3
DIVVS VR4 VR4 SR1
MULVV VR5 VR1 VR2
DIVVS VR5 VR5 SR1
ADDVV VR7 VR4 VR5 # VR7 = W^0_128 * y_odd[0] imaginary part
# y_even = fft(x[i], 1) = x[i] for i = 0~63
# load y_even real part
LV VR2 SR0
# load y_even imaginary part
LS SR1 SR0 8 # SR1 = 128
LV VR3 SR1
# y[i * 2] = y_even[0] + W^0_128 * y_odd[0] for i = 0~63
ADDVV VR4 VR2 VR6
ADDVV VR5 VR3 VR7
# y[i * 2 + 1] = y_even[0] - W^0_128 * y_odd[0] for i = 0~63
SUBVV VR6 VR2 VR6
SUBVV VR7 VR3 VR7
# store y real part to VDMEM 0~127
LS SR2 SR0 10 # SR2 = 2
SVWS VR4 SR0 SR2
LS SR3 SR0 2 # SR3 = 1
SVWS VR6 SR3 SR2
# store y imaginary part to VDMEM 128~255
LS SR1 SR0 8 # SR1 = 128
SVWS VR5 SR1 SR2
ADD SR1 SR1 SR3
SVWS VR7 SR1 SR2
# 32 4-point FFTs
# y_even = y[0:64], y_odd = y[64:128]
SLL SR7 SR7 SR3
LS SR1 SR0 11
BLE SR7 SR1 -61

HALT