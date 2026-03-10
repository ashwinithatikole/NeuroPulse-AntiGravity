`timescale 1ns / 1ps

module tb_mac_unit;

    // Parameters
    parameter DATA_WIDTH = 8;
    parameter ACC_WIDTH = 32;

    // Inputs
    reg clk;
    reg reset;
    reg en;
    reg signed [DATA_WIDTH-1:0] data_in;
    reg signed [DATA_WIDTH-1:0] weight_in;

    // Outputs
    wire signed [ACC_WIDTH-1:0] acc_out;

    // Instantiate the Unit Under Test (UUT)
    mac_unit #(
        .DATA_WIDTH(DATA_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .clk(clk),
        .reset(reset),
        .en(en),
        .data_in(data_in),
        .weight_in(weight_in),
        .acc_out(acc_out)
    );

    // Clock generation
    always #5 clk = ~clk;

    initial begin
        // Initialize Inputs
        clk = 0;
        reset = 1;
        en = 0;
        data_in = 0;
        weight_in = 0;

        // Wait 20 ns for global reset to finish
        #20;
        reset = 0;
        
        // Test Case 1: Simple multiplication and accumulation
        // 2 * 3 = 6
        #10;
        en = 1;
        data_in = 8'sd2;
        weight_in = 8'sd3;
        
        // Test Case 2: Accumulate another product
        // 6 + (4 * -5) = 6 - 20 = -14
        #10;
        data_in = 8'sd4;
        weight_in = -8'sd5;
        
        // Test Case 3: Disable and verify no change
        #10;
        en = 0;
        data_in = 8'sd10;
        weight_in = 8'sd10;
        
        // Test Case 4: Re-enable
        // -14 + (10 * 10) = 86
        #10;
        en = 1;
        
        // Wait and finish
        #20;
        $display("Test complete. Final acc_out: %d", acc_out);
        $finish;
    end
      
endmodule
