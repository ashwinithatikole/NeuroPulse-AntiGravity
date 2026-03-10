# NeuroPulse-AntiGravity

## Project Abstract: Team AntiGravity
NeuroPulse is a high-performance, low-power seizure detection engine designed for FPGA-based edge computing. Leveraging optimized 1D-Convolutional Neural Networks, Team AntiGravity has engineered a solution that balances aggressive hardware pruning with high temporal accuracy. Our implementation focuses on sub-100mW power profiles and minimal resource footprint for wearable medical diagnostics.

## Day 9 Verified Metrics
- **Power Consumption:** 108mW
- **LUT Usage:** 0.20%
- **Timing Slack:** 3.106ns

## Repository Structure
- `/src`: Core RTL Verilog source files.
- `/sim`: Simulation testbenches.
- `/const`: Xilinx Vivado hardware constraints.
- `/results`: Implementation results and screenshots.

## Deployment & Verification
The design is verified against the CHB-MIT Scalp EEG database, achieving real-time detection thresholds with minimal latency.
