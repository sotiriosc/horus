// rtl/horus_e3m6_acc_baseline.v — Phase 4b fair area baseline (synthesis-only).
//
// horus_e3m6_core (truncating 6-bit product) + minimal signed-32-bit
// exponent-aligned accumulator.  Same acc interface as horus_e3m6_mac for
// apples-to-apples area comparison of the width-preserving path.

`default_nettype none

module horus_e3m6_acc_baseline (
    input  wire               clk,
    input  wire               rst,
    input  wire        [9:0]  a,
    input  wire        [9:0]  b,
    input  wire               clear,
    input  wire               acc_en,
    output reg  signed [31:0] acc
);

    wire [9:0] prod_cw;
    horus_e3m6_core core (.a(a), .b(b), .result(prod_cw));

    wire        s_p = prod_cw[9];
    wire [2:0]  e_p = prod_cw[8:6];
    wire [5:0]  f_p = prod_cw[5:0];

    wire zero_p = (e_p == 3'd0) && (f_p == 6'd0);
    wire [6:0] M_p = zero_p ? 7'd0 :
                      (e_p == 3'd0) ? {1'b0, f_p} : {1'b1, f_p};
    wire [2:0] q_p = (e_p == 3'd0) ? 3'd1 : e_p;

    wire [3:0] shift_amt = {1'b0, q_p} - 4'd2;

    wire signed [31:0] P_signed = $signed({25'b0, M_p});
    wire signed [31:0] shifted_pos = P_signed <<< shift_amt;
    wire signed [31:0] shifted_neg = -shifted_pos;
    wire signed [31:0] addend = s_p ? shifted_neg : shifted_pos;

    wire signed [31:0] acc_next =
        clear ? 32'sd0 :
        (acc_en && !zero_p) ? (acc + addend) : acc;

    always @(posedge clk) begin
        if (rst)
            acc <= 32'sd0;
        else
            acc <= acc_next;
    end

endmodule

`default_nettype wire
