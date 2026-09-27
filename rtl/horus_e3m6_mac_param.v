// rtl/horus_e3m6_mac_param.v — Width-parameterized E3M6 MAC (Track B).
//
// Phase-4b verified netlist lives in horus_e3m6_mac.v (untouched).
// horus_e3m6_mac_w32.v wraps this module at ACC_WIDTH=32 for regression.

`default_nettype none

module horus_e3m6_mac_param #(
    parameter integer ACC_WIDTH = 32,
    parameter integer ACC_SHIFT_MAX = 12
) (
    input  wire                        clk,
    input  wire                        rst,
    input  wire                 [9:0]  a,
    input  wire                 [9:0]  b,
    input  wire                        clear,
    input  wire                        acc_en,
    output wire                        prod_sign,
    output wire               [13:0]   prod_P,
    output wire               [3:0]    prod_w,
    output reg  signed [ACC_WIDTH-1:0] acc
);

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

    wire [3:0] shift_amt = prod_w - 4'd2;

    // Shift math matches horus_e3m6_mac.v (14-bit P, max shift 12); acc width varies.
    wire signed [31:0] P_signed = $signed({18'b0, prod_P});
    wire signed [31:0] shifted_pos = P_signed <<< shift_amt;
    wire signed [31:0] shifted_neg = -shifted_pos;
    wire signed [31:0] addend32 = prod_sign ? shifted_neg : shifted_pos;

    wire signed [ACC_WIDTH-1:0] addend =
        (ACC_WIDTH <= 32) ? $signed(addend32[ACC_WIDTH-1:0]) :
        {{(ACC_WIDTH-32){addend32[31]}}, addend32};

    wire signed [ACC_WIDTH-1:0] acc_next =
        clear ? {ACC_WIDTH{1'b0}} :
        (acc_en && !p_zero) ? (acc + addend) : acc;

    always @(posedge clk) begin
        if (rst)
            acc <= {ACC_WIDTH{1'b0}};
        else
            acc <= acc_next;
    end

endmodule

`default_nettype wire
