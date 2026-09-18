// rtl/horus_array_4x4.v — Track C wiring harness (16× horus_tile_v2).

`default_nettype none

module horus_array_4x4 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        mode,

    input  wire [9:0]  op_a_00, input  wire [9:0]  op_b_00,
    input  wire [9:0]  op_a_01, input  wire [9:0]  op_b_01,
    input  wire [9:0]  op_a_02, input  wire [9:0]  op_b_02,
    input  wire [9:0]  op_a_03, input  wire [9:0]  op_b_03,
    input  wire [9:0]  op_a_10, input  wire [9:0]  op_b_10,
    input  wire [9:0]  op_a_11, input  wire [9:0]  op_b_11,
    input  wire [9:0]  op_a_12, input  wire [9:0]  op_b_12,
    input  wire [9:0]  op_a_13, input  wire [9:0]  op_b_13,
    input  wire [9:0]  op_a_20, input  wire [9:0]  op_b_20,
    input  wire [9:0]  op_a_21, input  wire [9:0]  op_b_21,
    input  wire [9:0]  op_a_22, input  wire [9:0]  op_b_22,
    input  wire [9:0]  op_a_23, input  wire [9:0]  op_b_23,
    input  wire [9:0]  op_a_30, input  wire [9:0]  op_b_30,
    input  wire [9:0]  op_a_31, input  wire [9:0]  op_b_31,
    input  wire [9:0]  op_a_32, input  wire [9:0]  op_b_32,
    input  wire [9:0]  op_a_33, input  wire [9:0]  op_b_33,

    output wire [12:0] nfe_out_00, output wire [12:0] nfe_out_01,
    output wire [12:0] nfe_out_02, output wire [12:0] nfe_out_03,
    output wire [12:0] nfe_out_10, output wire [12:0] nfe_out_11,
    output wire [12:0] nfe_out_12, output wire [12:0] nfe_out_13,
    output wire [12:0] nfe_out_20, output wire [12:0] nfe_out_21,
    output wire [12:0] nfe_out_22, output wire [12:0] nfe_out_23,
    output wire [12:0] nfe_out_30, output wire [12:0] nfe_out_31,
    output wire [12:0] nfe_out_32, output wire [12:0] nfe_out_33
);

    horus_tile_v2 t00 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_00), .op_b(op_b_00), .nfe_out(nfe_out_00));
    horus_tile_v2 t01 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_01), .op_b(op_b_01), .nfe_out(nfe_out_01));
    horus_tile_v2 t02 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_02), .op_b(op_b_02), .nfe_out(nfe_out_02));
    horus_tile_v2 t03 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_03), .op_b(op_b_03), .nfe_out(nfe_out_03));
    horus_tile_v2 t10 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_10), .op_b(op_b_10), .nfe_out(nfe_out_10));
    horus_tile_v2 t11 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_11), .op_b(op_b_11), .nfe_out(nfe_out_11));
    horus_tile_v2 t12 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_12), .op_b(op_b_12), .nfe_out(nfe_out_12));
    horus_tile_v2 t13 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_13), .op_b(op_b_13), .nfe_out(nfe_out_13));
    horus_tile_v2 t20 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_20), .op_b(op_b_20), .nfe_out(nfe_out_20));
    horus_tile_v2 t21 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_21), .op_b(op_b_21), .nfe_out(nfe_out_21));
    horus_tile_v2 t22 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_22), .op_b(op_b_22), .nfe_out(nfe_out_22));
    horus_tile_v2 t23 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_23), .op_b(op_b_23), .nfe_out(nfe_out_23));
    horus_tile_v2 t30 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_30), .op_b(op_b_30), .nfe_out(nfe_out_30));
    horus_tile_v2 t31 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_31), .op_b(op_b_31), .nfe_out(nfe_out_31));
    horus_tile_v2 t32 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_32), .op_b(op_b_32), .nfe_out(nfe_out_32));
    horus_tile_v2 t33 (.clk(clk), .rst_n(rst_n), .mode(mode), .op_a(op_a_33), .op_b(op_b_33), .nfe_out(nfe_out_33));

endmodule

`default_nettype wire
