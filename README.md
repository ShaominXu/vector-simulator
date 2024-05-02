# Vector Simulator

ECE-GY-9413 Course Project

- Shaomin Xu, sx2311

## Fuction Simulator
### Input
- Code.asm
- SDMEM.txt
- VDMEM.txt
### Output
- SRF.txt
- SDMEMOP.txt
- VDMEMOP.txt
- trace.txt (optional)
```
cd script
python sx2311_funcsimulator.py --iodir <path/to/iodir> [--trace]
```

The optional `--trace` flag, if provided, will generate a `trace.txt` in the
`<iodir>` folder. This trace is required to execute timing simulator.

## Timing Simulator
### Input
- trace.txt
### Output
- time.txt
```
cd script
python sx2311_timingsimulator.py --iodir <path/to/iodir> [--pipelined]
```
The optional `--pipelined` flag, if provided, will enable pipelined instruction 
start-up optimization.

## More details are in `script/README.md`.