`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// Module   : skpr_block_detect_rr
// Purpose  : Rule 5 detect + argmax / repair-mask for repair-and-replay.
//            flag / e_max / e_second / gap bit-identical to skpr_block_detect
//            / skpr_golden (strict gap > T; equal-top ⇒ no flag).
// ============================================================================

module skpr_block_detect_rr (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        valid_in,
    input  wire [12:0] in_0,
    input  wire [12:0] in_1,
    input  wire [12:0] in_2,
    input  wire [12:0] in_3,
    input  wire [12:0] in_4,
    input  wire [12:0] in_5,
    input  wire [12:0] in_6,
    input  wire [12:0] in_7,
    input  wire        t_we,
    input  wire [5:0]  t_in,

    output reg         valid_out,
    output reg         flag_out,
    output reg  [5:0]  e_max_out,
    output reg  [5:0]  e_second_out,
    output reg  [5:0]  gap_out,
    output reg  [2:0]  argmax_out,
    output reg         unique_max_out,
    output reg  [7:0]  repair_mask_out
);

    reg [5:0] T;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) T <= 6'd0;
        else if (t_we) T <= t_in;
    end

    wire [5:0] e0 = in_0[11:6];
    wire [5:0] e1 = in_1[11:6];
    wire [5:0] e2 = in_2[11:6];
    wire [5:0] e3 = in_3[11:6];
    wire [5:0] e4 = in_4[11:6];
    wire [5:0] e5 = in_5[11:6];
    wire [5:0] e6 = in_6[11:6];
    wire [5:0] e7 = in_7[11:6];

    wire [5:0] lv1_01   = (e0   >= e1  ) ? e0   : e1;
    wire [5:0] lv1_23   = (e2   >= e3  ) ? e2   : e3;
    wire [5:0] lv1_45   = (e4   >= e5  ) ? e4   : e5;
    wire [5:0] lv1_67   = (e6   >= e7  ) ? e6   : e7;
    wire [5:0] lv2_0123 = (lv1_01 >= lv1_23) ? lv1_01 : lv1_23;
    wire [5:0] lv2_4567 = (lv1_45 >= lv1_67) ? lv1_45 : lv1_67;
    wire [5:0] e_max    = (lv2_0123 >= lv2_4567) ? lv2_0123 : lv2_4567;

    wire [5:0] lo1_01 = (e0   >= e1  ) ? e1   : e0;
    wire [5:0] lo1_23 = (e2   >= e3  ) ? e3   : e2;
    wire [5:0] lo1_45 = (e4   >= e5  ) ? e5   : e4;
    wire [5:0] lo1_67 = (e6   >= e7  ) ? e7   : e6;
    wire [5:0] lo2_0123 = (lv1_01 >= lv1_23) ? lv1_23 : lv1_01;
    wire [5:0] lo2_4567 = (lv1_45 >= lv1_67) ? lv1_67 : lv1_45;
    wire [5:0] lo3 = (lv2_0123 >= lv2_4567) ? lv2_4567 : lv2_0123;
    wire win_l2_left = (lv2_0123 >= lv2_4567);
    wire win_l1_left = win_l2_left ? (lv1_01 >= lv1_23) : (lv1_45 >= lv1_67);
    wire [5:0] lo2_win = win_l2_left ? lo2_0123 : lo2_4567;
    wire [5:0] lo1_win = win_l2_left
                       ? (win_l1_left ? lo1_01 : lo1_23)
                       : (win_l1_left ? lo1_45 : lo1_67);
    wire [5:0] m01 = (lo3 >= lo2_win) ? lo3 : lo2_win;
    wire [5:0] e_second = (m01 >= lo1_win) ? m01 : lo1_win;

    wire [5:0] gap  = e_max - e_second;
    wire       flag = (gap > T);

    // Unique arg-max index (lowest index on ties — but flag requires unique)
    wire [3:0] nmax = (e0 == e_max) + (e1 == e_max) + (e2 == e_max) + (e3 == e_max)
                    + (e4 == e_max) + (e5 == e_max) + (e6 == e_max) + (e7 == e_max);
    wire unique_max = (nmax == 4'd1);

    reg [2:0] argmax;
    always @(*) begin
        if      (e0 == e_max) argmax = 3'd0;
        else if (e1 == e_max) argmax = 3'd1;
        else if (e2 == e_max) argmax = 3'd2;
        else if (e3 == e_max) argmax = 3'd3;
        else if (e4 == e_max) argmax = 3'd4;
        else if (e5 == e_max) argmax = 3'd5;
        else if (e6 == e_max) argmax = 3'd6;
        else                  argmax = 3'd7;
    end

    wire [7:0] mask = (flag && unique_max) ? (8'b1 << argmax) : 8'b0;

    always @(posedge clk) begin
        if (!rst_n) begin
            valid_out       <= 1'b0;
            flag_out        <= 1'b0;
            e_max_out       <= 6'd0;
            e_second_out    <= 6'd0;
            gap_out         <= 6'd0;
            argmax_out      <= 3'd0;
            unique_max_out  <= 1'b0;
            repair_mask_out <= 8'd0;
        end else begin
            valid_out       <= valid_in;
            flag_out        <= flag;
            e_max_out       <= e_max;
            e_second_out    <= e_second;
            gap_out         <= gap;
            argmax_out      <= argmax;
            unique_max_out  <= unique_max;
            repair_mask_out <= mask;
        end
    end

endmodule
