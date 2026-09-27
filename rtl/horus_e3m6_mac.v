// rtl/horus_e3m6_mac.v — Phase 4b width-preserving E3M6 MAC primitive.
//
// Arithmetic contract (binding, docs/JACOBI_VERDICT.md Phase 4b):
//   - No input flush: subnormals participate (M=f, q=1 when e=0,f!=0).
//   - Full 14-bit product P = M_a * M_b exposed (no 6-bit truncation).
//   - Exponent-aligned signed-32 accumulate on block-relative addends ±P·2^(w−2),
//     w = q_a + q_b.
//
// Combinational product outputs + registered accumulator (clear/acc_en).

`default_nettype none

module horus_e3m6_mac (
    input  wire               clk,
    input  wire               rst,
    input  wire        [9:0]  a,
    input  wire        [9:0]  b,
    input  wire               clear,
    input  wire               acc_en,
    output wire               prod_sign,
    output wire [13:0]        prod_P,
    output wire [3:0]           prod_w,
    output reg  signed [31:0] acc
);

    // ── Unpack operands (no flush) ───────────────────────────────────────────
    wire        s_a = a[9];
    wire [2:0]  e_a = a[8:6];
    wire [5:0]  f_a = a[5:0];
    wire        s_b = b[9];
    wire [2:0]  e_b = b[8:6];
    wire [5:0]  f_b = b[5:0];

    wire zero_a = (e_a == 3'd0) && (f_a == 6'd0);
    wire zero_b = (e_b == 3'd0) && (f_b == 6'd0);

    wire [6:0] M_a = zero_a ? 7'd0 :
                     (e_a == 3'd0) ? {1'b0, f_a} : {1'b1, f_a};
    wire [6:0] M_b = zero_b ? 7'd0 :
                     (e_b == 3'd0) ? {1'b0, f_b} : {1'b1, f_b};

    wire [2:0] q_a = (e_a == 3'd0) ? 3'd1 : e_a;
    wire [2:0] q_b = (e_b == 3'd0) ? 3'd1 : e_b;

    wire        p_zero = zero_a | zero_b | (M_a == 7'd0) | (M_b == 7'd0);
    wire [13:0] P      = M_a * M_b;
    wire [3:0]  w_sum  = {1'b0, q_a} + {1'b0, q_b};

    assign prod_sign = s_a ^ s_b;
    assign prod_P    = p_zero ? 14'd0 : P;
    assign prod_w    = p_zero ? 4'd0  : w_sum;

    // ── Exponent-aligned accumulate: ±P << (w−2) ─────────────────────────────
    wire [3:0] shift_amt = prod_w - 4'd2;

    wire signed [31:0] P_signed = $signed({18'b0, prod_P});
    wire signed [31:0] shifted_pos = P_signed <<< shift_amt;
    wire signed [31:0] shifted_neg = -shifted_pos;
    wire signed [31:0] addend = prod_sign ? shifted_neg : shifted_pos;

    wire signed [31:0] acc_next =
        clear ? 32'sd0 :
        (acc_en && !p_zero) ? (acc + addend) : acc;

    always @(posedge clk) begin
        if (rst)
            acc <= 32'sd0;
        else
            acc <= acc_next;
    end

endmodule

`default_nettype wire
