module weight_rom_layer1 #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 6, // 48 weights total (2^6 = 64)
    parameter DEPTH = 48
)(
    input wire clk,
    input wire [ADDR_WIDTH-1:0] addr,
    output reg signed [DATA_WIDTH-1:0] weight_out
);

    reg signed [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    initial begin
        // Template for initialization. Use weights_layer1.hex generated from Day 5
        $readmemh("weights_layer1.hex", mem);
    end

    always @(posedge clk) begin
        weight_out <= mem[addr];
    end

endmodule
