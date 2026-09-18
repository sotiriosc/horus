// rtl/horus_e3m6_acc_baseline_w36.v

`default_nettype none

module horus_e3m6_acc_baseline_w36 (
    input  wire               clk,
    input  wire               rst,
    input  wire        [9:0]  a,
    input  wire        [9:0]  b,
    input  wire               clear,
    input  wire               acc_en,
    output reg signed [35:0]  acc
);
    horus_e3m6_acc_baseline_param #(.ACC_WIDTH(36)) u_base (
        .clk(clk), .rst(rst), .a(a), .b(b), .clear(clear), .acc_en(acc_en), .acc(acc)
    );
endmodule

`default_nettype wire
