

## Run

```
cd script
```

### Part 1: Function Simulator
##### Test ISA

```shell
python sx2311_funcsimulator.py --iodir ../IO_ISA
```
If no error occurs, verification is passed.

More details are in `IO_ISA/README.md`, 
including a short description of the test program and instructions to show completeness.
#### Test Dot Product

```shell
python sx2311_funcsimulator.py --iodir ../IO_Dot_Product
```
The result is stored in VDMEM[2048]. If the result equals to SDMEM[5], verification is passed.

### Part 2: Function Simulator

Store the result in to address 0 of VDMEM.

#### Test Fully Connected Layer

```shell
python sx2311_funcsimulator.py --iodir ../IO_FCC
```

#### Test Convolution Layer

```shell
python sx2311_funcsimulator.py --iodir ../IO_Conv
```

#### Test Fast Fourirer Transform

```shell
python sx2311_funcsimulator.py --iodir ../IO_FFT
```
The real part of the result is stored in VDMEM[0:63] and the imaginary part is stored in VDMEM[64:127].

### Part 3: Timing Simulator
#### Get the dynamic flow - trace.txt
```shell
python sx2311_funcsimulator.py --iodir ../IO_Dot_Product --trace
python sx2311_funcsimulator.py --iodir ../IO_FCC --trace
python sx2311_funcsimulator.py --iodir ../IO_Conv --trace
```

#### Get performance - time.txt
```shell
python sx2311_timingsimulator.py --iodir ../IO_Dot_Product
python sx2311_timingsimulator.py --iodir ../IO_FCC
python sx2311_timingsimulator.py --iodir ../IO_Conv
```
##### Optimization: Pipelined Instruction Start-up
```shell
python sx2311_timingsimulator.py --iodir ../IO_Dot_Product --pipelined
python sx2311_timingsimulator.py --iodir ../IO_FCC --pipelined
python sx2311_timingsimulator.py --iodir ../IO_Conv --pipelined
```

