# Vector Simulator

## Test ISA

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_ISA
```

## Test Dot Product

```shell
cd script
python sx2311_funcsimulator.py --iodir ../IO_Dot_Product
```

### Generate Input Vector

Create input vector {0, 1, ..., 499} and save it to `generated_vector.txt`. Then copy it to `VDMEM.txt`.

```shell
cd utils
python generated_vector.py
```
