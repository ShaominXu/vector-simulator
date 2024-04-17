# real part of input x is stored in VDMEM 0~127
# imaginary part of input x is stored in VDMEM 128~255
# real part of weights w is stored in VDMEM 256~319
# imaginary part of weights w is stored in VDMEM 320~383
CVM
# 64 2-point FFTs
LS SR7 SR0 6 # SR7 = 64
LS SR2 SR0 1 # SR2 = 1
MTCL SR2 # SR2 is k range
# load w
LS SR1 SR0 8 # SR1 = 256
LVWS VR0 SR1 SR7 # VR0 = w real part
LS SR1 SR0 9 # SR1 = 320
LVWS VR1 SR1 SR7 # VR1 = w imaginary part
LS SR4 SR0 0 # SR4 = 0 is offset for load y
# load y_odd
LS SR1 SR0 6 # SR1 = 64
ADD SR5 SR4 SR1
LV VR2 SR5 # VR2 = y_odd real part
LS SR1 SR0 7 # SR1 = 128
ADD SR5 SR5 SR1
LV VR3 SR5 # VR3 = y_odd imaginary part
# w * y_odd
LS SR1 SR0 15 # SR1 = 1000
MULVV VR4 VR0 VR2 # VR4 = w_real * y_odd_real
DIVVS VR4 VR4 SR1 # VR4 = w_real * y_odd_real / 1000
MULVV VR5 VR1 VR3 # VR5 = w_imag * y_odd_imag
DIVVS VR5 VR5 SR1 # VR5 = w_imag * y_odd_imag / 1000
SUBVV VR6 VR4 VR5 # w * y_odd real part
MULVV VR4 VR0 VR3 # VR4 = w_real * y_odd_imag
DIVVS VR4 VR4 SR1 # VR4 = w_real * y_odd_imag / 1000
MULVV VR5 VR1 VR2 # VR5 = w_imag * y_odd_real
DIVVS VR5 VR5 SR1 # VR5 = w_imag * y_odd_real / 1000
ADDVV VR7 VR4 VR5 # w * y_odd imaginary part
# load y_even
LS SR1 SR0 7 # SR1 = 128
LV VR2 SR4 # VR2 = y_even real part
ADD SR5 SR4 SR1
LV VR3 SR5 # VR3 = y_even imaginary part
# y_even + w * y_odd
ADDVV VR4 VR2 VR6 # VR4 = y_even_real + w * y_odd real
ADDVV VR5 VR3 VR7 # VR5 = y_even_imag + w * y_odd imag
# y_even - w * y_odd
SUBVV VR6 VR2 VR6 # VR6 = y_even_real - w * y_odd real
SUBVV VR7 VR3 VR7 # VR7 = y_even_imag - w * y_odd imag
# store y_even + w * y_odd
LS SR1 SR0 10 # SR1 = 384
ADD SR5 SR1 SR4
ADD SR5 SR5 SR4 # SR4 * 2 is offset for store y
SV VR4 SR5 # y_even + w * y_odd real part
ADD SR5 SR5 SR2
SV VR6 SR5 # y_even - w * y_odd real part
LS SR1 SR0 12 # SR1 = 512
ADD SR5 SR1 SR4
ADD SR5 SR5 SR4
SV VR5 SR5 # y_even + w * y_odd imaginary part
ADD SR5 SR5 SR2
SV VR7 SR5 # y_even - w * y_odd imaginary part
# loop for i
ADD SR4 SR4 SR2
LS SR1 SR0 6 # SR1 = 64
BLT SR4 SR1 -46 # jump to # load y_odd
# save y from address 384 to 0 after each stage
LS SR1 SR0 10 # SR1 = 384
LS SR3 SR0 0 # SR3 = 0
LS SR5 SR0 6 # SR5 = 64
LS SR6 SR0 14 # SR6 = 640
MTCL SR5
LV VR0 SR1
SV VR0 SR3
ADD SR1 SR1 SR5
ADD SR3 SR3 SR5
BLT SR1 SR6 -4
# loop stage
ADD SR2 SR2 SR2
MTCL SR2
LS SR1 SR0 1 # SR1 = 1
SRL SR7 SR7 SR1
LS SR1 SR0 6 # SR1 = 64
BLE SR2 SR1 -68 # jump to # load w
HALT