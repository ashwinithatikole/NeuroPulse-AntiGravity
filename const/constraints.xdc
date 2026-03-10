# Clock Definition - 100MHz (10ns period)
# ZedBoard: Y9 | Zybo: L16
create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]

# LED Assignment - Seizure Alert
# Map the MSB of data_out or a specific 'alert' signal to an LED
# ZedBoard LD0: T22 | Zybo LED0: M14
set_property PACKAGE_PIN T22 [get_ports seizure_alert]
set_property IOSTANDARD LVCMOS33 [get_ports seizure_alert]

# Note: Adjust PACKAGE_PIN based on your specific board model.
# ZedBoard Buttons/Switches for Reset (P16/G1) etc.
set_property PACKAGE_PIN P16 [get_ports reset]
set_property IOSTANDARD LVCMOS33 [get_ports reset]
