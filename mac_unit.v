module mac_unit #(
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH = 32
)(
    input wire clk,
    input wire reset,
    input wire en,
    input wire signed [DATA_WIDTH-1:0] data_in,
    input wire signed [DATA_WIDTH-1:0] weight_in,
    output reg signed [ACC_WIDTH-1:0] acc_out
);

    wire signed [(2*DATA_WIDTH)-1:0] product;

    assign product = data_in * weight_in;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            acc_out <= {ACC_WIDTH{1'b0}};
        end else if (en) begin
            acc_out <= acc_out + product;
        end
    end

endmodule
