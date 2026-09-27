// rtl/horus_array_2x2.v — Track C wiring harness (4× horus_tile_v2).

`default_nettype none

module horus_array_2x2 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        mode,

    input  wire [9:0]  op_a_00, input  wire [9:0]  op_b_00,
    input  wire [9:0]  op_a_01, input  wire [9:0]  op_b_01,
    input  wire [9:0]  op_a_10, input  wire [9:0]  op_b_10,
    input  wire [9:0]  op_a_11, input  wire [9:0]  op_b_11,

    output wire [12:0] nfe_out_00,
    output wire [12:0] nfe_out_01,
    output wire [12:0] nfe_out_10,
    output wire [12:0] nfe_out_11
);

    horus_tile_v2 t00 (.clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a(op_a_00), .op_b(op_b_00), .nfe_out(nfe_out_00));
    horus_tile_v2 t01 (.clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a(op_a_01), .op_b(op_b_01), .nfe_out(nfe_out_01));
    horus_tile_v2 t10 (.clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a(op_a_10), .op_b(op_b_10), .nfe_out(nfe_out_10));
    horus_tile_v2 t11 (.clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a(op_a_11), .op_b(op_b_11), .nfe_out(nfe_out_11));

endmodule

`default_nettype wire
