// rtl/horus_e3m6_acc_baseline_w32.v

`default_nettype none

module horus_e3m6_acc_baseline_w32 (
    input  wire               clk,
    input  wire               rst,
    input  wire        [9:0]  a,
    input  wire        [9:0]  b,
    input  wire               clear,
    input  wire               acc_en,
    output reg signed [31:0]  acc
);
    horus_e3m6_acc_baseline_param #(.ACC_WIDTH(32)) u_base (
        .clk(clk), .rst(rst), .a(a), .b(b), .clear(clear), .acc_en(acc_en), .acc(acc)
    );
endmodule

`default_nettype wire
