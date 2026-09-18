// rtl/horus_e3m6_acc_baseline_param.v — Fair baseline with parameterized acc width.

`default_nettype none

module horus_e3m6_acc_baseline_param #(
    parameter integer ACC_WIDTH = 32
) (
    input  wire                        clk,
    input  wire                        rst,
    input  wire                 [9:0]  a,
    input  wire                 [9:0]  b,
    input  wire                        clear,
    input  wire                        acc_en,
    output reg  signed [ACC_WIDTH-1:0] acc
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
    wire signed [31:0] addend32 = s_p ? shifted_neg : shifted_pos;

    wire signed [ACC_WIDTH-1:0] addend =
        (ACC_WIDTH <= 32) ? $signed(addend32[ACC_WIDTH-1:0]) :
        {{(ACC_WIDTH-32){addend32[31]}}, addend32};

    wire signed [ACC_WIDTH-1:0] acc_next =
        clear ? {ACC_WIDTH{1'b0}} :
        (acc_en && !zero_p) ? (acc + addend) : acc;

    always @(posedge clk) begin
        if (rst)
            acc <= {ACC_WIDTH{1'b0}};
        else
            acc <= acc_next;
    end

endmodule

`default_nettype wire
