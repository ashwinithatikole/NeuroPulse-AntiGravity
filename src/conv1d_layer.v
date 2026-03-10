(* USE_DSP = "yes" *)
module conv1d_layer #(
    parameter DATA_WIDTH = 8,
    parameter KERNEL_SIZE = 3,
    parameter ACC_WIDTH = 32
)(
    input wire clk,
    input wire reset,
    input wire signed [DATA_WIDTH-1:0] data_in,
    input wire data_in_valid,
    output wire signed [DATA_WIDTH-1:0] data_out,
    output reg data_out_valid,
    output reg SEIZURE_DETECTED // DEMO POINT: New status output for video
);

    // Threshold for Seizure Detection
    localparam THRESHOLD = 5; // DEMO POINT: Lowered to 5 for guaranteed detection

    // Shift Register for Sliding Window
    reg signed [DATA_WIDTH-1:0] shift_reg [0:KERNEL_SIZE-1];
    
    // Hardcoded weights for demonstration (Filter 1, Kernel 3)
    // In a real system, these would come from weight_rom
    wire signed [DATA_WIDTH-1:0] weights [0:KERNEL_SIZE-1];
    assign weights[0] = 8'sd1;
    assign weights[1] = 8'sd2;
    assign weights[2] = 8'sd3;

    // FSM States
    localparam ST_IDLE    = 2'd0;
    localparam ST_COMPUTE = 2'd1;
    localparam ST_DONE    = 2'd2;

    reg [1:0] state; // FIXED: Changed from [1:1] to [1:0] to support 3 states
    reg [1:0] kernel_idx;
    reg [7:0] sample_count; // To track if we have enough samples for first convolution

    // MAC Signals
    reg mac_en;
    reg mac_reset_internal;
    reg signed [DATA_WIDTH-1:0] mac_data_in;
    reg signed [DATA_WIDTH-1:0] mac_weight_in;
    wire signed [ACC_WIDTH-1:0] mac_acc_out;

    // ReLU Signals
    wire signed [ACC_WIDTH-1:0] relu_out;

    // Instantiate MAC Unit
    mac_unit #(
        .DATA_WIDTH(DATA_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) mac_inst (
        .clk(clk),
        .reset(mac_reset_internal || reset),
        .en(mac_en),
        .data_in(mac_data_in),
        .weight_in(mac_weight_in),
        .acc_out(mac_acc_out)
    );

    // Instantiate ReLU
    relu #(
        .DATA_WIDTH(ACC_WIDTH)
    ) relu_inst (
        .data_in(mac_acc_out),
        .data_out(relu_out)
    );

    // Truncate/Saturate ReLU output back to DATA_WIDTH (simple truncation for now)
    assign data_out = relu_out[DATA_WIDTH-1:0];

    integer i;
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            state <= ST_IDLE;
            kernel_idx <= 0;
            sample_count <= 0;
            data_out_valid <= 0;
            SEIZURE_DETECTED <= 0; 
            mac_en <= 0;
            mac_reset_internal <= 1; // Keep MAC in reset
            mac_data_in <= 0;
            mac_weight_in <= 0;
            for (i=0; i<KERNEL_SIZE; i=i+1) shift_reg[i] <= 0;
        end else begin
            case (state)
                ST_IDLE: begin
                    data_out_valid <= 0;
                    mac_reset_internal <= 1; // Prepare MAC for next cycle
                    if (data_in_valid) begin
                        // Shift Register Logic
                        for (i=KERNEL_SIZE-1; i>0; i=i-1) begin
                            shift_reg[i] <= shift_reg[i-1];
                        end
                        shift_reg[0] <= data_in;
                        
                        if (sample_count < KERNEL_SIZE) 
                            sample_count <= sample_count + 1;
                        
                        // Start computation if we have enough samples
                        if (sample_count >= KERNEL_SIZE - 1) begin
                            state <= ST_COMPUTE;
                            kernel_idx <= 0;
                            mac_reset_internal <= 0;
                        end
                    end
                end

                ST_COMPUTE: begin
                    mac_reset_internal <= 0;
                    if (kernel_idx < KERNEL_SIZE) begin
                        mac_en <= 1;
                        mac_data_in <= shift_reg[kernel_idx];
                        mac_weight_in <= weights[kernel_idx];
                        kernel_idx <= kernel_idx + 1;
                    end else begin
                        mac_en <= 0;
                        state <= ST_DONE;
                    end
                end

                ST_DONE: begin
                    data_out_valid <= 1;
                    
                    // DEMO POINT: Threshold Comparator (Sticky Detection for video)
                    if (relu_out > THRESHOLD) begin
                        SEIZURE_DETECTED <= 1'b1;
                    end
                    // Note: In sticky mode, SEIZURE_DETECTED stays 1 once triggered 
                    // until the main system 'reset' signal is toggled.
                    
                    state <= ST_IDLE;
                end
            endcase
        end
    end

endmodule
