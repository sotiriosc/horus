// rtl/horus_e3m6_mac_w34.v — 34-bit accumulator wrapper (N=32 scope).

`default_nettype none

module horus_e3m6_mac_w34 (
    input  wire               clk,
    input  wire               rst,
    input  wire        [9:0]  a,
    input  wire        [9:0]  b,
    input  wire               clear,
    input  wire               acc_en,
    output wire               prod_sign,
    output wire [13:0]        prod_P,
    output wire [3:0]         prod_w,
    output wire signed [33:0] acc
);
    horus_e3m6_mac_param #(.ACC_WIDTH(34)) u_mac (
        .clk(clk), .rst(rst), .a(a), .b(b),
        .clear(clear), .acc_en(acc_en),
        .prod_sign(prod_sign), .prod_P(prod_P), .prod_w(prod_w),
        .acc(acc)
    );
endmodule

`default_nettype wire
