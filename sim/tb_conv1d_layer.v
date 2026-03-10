`timescale 1ns / 1ps

module tb_conv1d_layer;
    reg clk;
    reg reset;
    reg [7:0] data_in;
    reg data_in_valid;
    wire [7:0] data_out;
    wire data_out_valid;
    wire SEIZURE_DETECTED;

    // 1. Clock Generation (10ns Period)
    initial clk = 0;
    always #5 clk = ~clk;

    // 2. Unit Under Test
    conv1d_layer uut (
        .clk(clk),
        .reset(reset),
        .data_in(data_in),
        .data_in_valid(data_in_valid),
        .data_out(data_out),
        .data_out_valid(data_out_valid),
        .SEIZURE_DETECTED(SEIZURE_DETECTED)
    );

    // 3. Continuous Data Streaming
    initial begin
        // Startup and Reset
        reset = 1; data_in = 0; data_in_valid = 0;
        #50 reset = 0; 
        #20;

        // Start Streaming Continuous Data
        data_in_valid = 1;
        
        // Feed specific values to ensure a quick and visible detection
        // Weights are 1, 2, 3. Threshold is 5.
        // Sample 1: 10
        // Sample 2: 20
        // Sample 3: 30
        // Sum will be (10*3 + 20*2 + 30*1) = 100 > 5 -> ALERT!
        
        forever begin
            @(posedge clk);
            data_in = data_in + 8'd10; // Jump by 10 for rapid movement
            
            // Console feedback
            if (data_out_valid) begin
                $display(">>> DEMO: DATA_OUT=%d | ALERT=%b <<<", data_out, SEIZURE_DETECTED);
            end
        end
    end

    // Safety timeout to prevent infinite simulation
    initial #2000 $finish; 

endmodule
