# Vector Simulator

## Part 1
### Test ISA

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_ISA
```
If no error occurs, verification is passed.

More details are in `IO_ISA/README.md`, 
including a short description of the test program and instructions to show completeness.
### Test Dot Product

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_Dot_Product
```
The result is stored in VDMEM[2048]. If the result equals to SDMEM[5], verification is passed.
## Part 2

Store the result in to address 0 of VDMEM.

### Test Fully Connected Layer

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_FCC
```

## Test Convolution Layer

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_Conv
```

## Test Fast Fourirer Transform

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_FFT
```
The real part of the result is stored in VDMEM[0:63] and the imaginary part is stored in VDMEM[64:127].