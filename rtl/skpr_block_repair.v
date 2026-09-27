`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// Combinational unique-arg-max SAT/KEEP repair

module skpr_block_repair (
    input  wire [12:0] in_0,
    input  wire [12:0] in_1,
    input  wire [12:0] in_2,
    input  wire [12:0] in_3,
    input  wire [12:0] in_4,
    input  wire [12:0] in_5,
    input  wire [12:0] in_6,
    input  wire [12:0] in_7,
    input  wire        det_flag,
    input  wire [5:0]  det_e_second,
    input  wire [2:0]  det_argmax_idx,
    input  wire [7:0]  det_repair_mask,
    input  wire [1:0]  repair_mode,

    output wire [12:0] out_0,
    output wire [12:0] out_1,
    output wire [12:0] out_2,
    output wire [12:0] out_3,
    output wire [12:0] out_4,
    output wire [12:0] out_5,
    output wire [12:0] out_6,
    output wire [12:0] out_7,
    output wire        repair_applied,
    output wire [3:0]  repair_count
);

    localparam [1:0] REPAIR_NONE = 2'd0;
    localparam [1:0] REPAIR_SAT  = 2'd1;
    localparam [1:0] REPAIR_KEEP = 2'd2;
    localparam [5:0] MANT_MAX    = 6'b111111;

    wire do_repair = det_flag && (repair_mode != REPAIR_NONE) && (|det_repair_mask);
    wire is_sat    = (repair_mode == REPAIR_SAT);
    wire is_keep   = (repair_mode == REPAIR_KEEP);

    wire [12:0] sat0  = {in_0[12],  det_e_second, MANT_MAX};
    wire [12:0] keep0 = {in_0[12],  det_e_second, in_0[5:0]};
    wire [12:0] sat1  = {in_1[12],  det_e_second, MANT_MAX};
    wire [12:0] keep1 = {in_1[12],  det_e_second, in_1[5:0]};
    wire [12:0] sat2  = {in_2[12],  det_e_second, MANT_MAX};
    wire [12:0] keep2 = {in_2[12],  det_e_second, in_2[5:0]};
    wire [12:0] sat3  = {in_3[12],  det_e_second, MANT_MAX};
    wire [12:0] keep3 = {in_3[12],  det_e_second, in_3[5:0]};
    wire [12:0] sat4  = {in_4[12],  det_e_second, MANT_MAX};
    wire [12:0] keep4 = {in_4[12],  det_e_second, in_4[5:0]};
    wire [12:0] sat5  = {in_5[12],  det_e_second, MANT_MAX};
    wire [12:0] keep5 = {in_5[12],  det_e_second, in_5[5:0]};
    wire [12:0] sat6  = {in_6[12],  det_e_second, MANT_MAX};
    wire [12:0] keep6 = {in_6[12],  det_e_second, in_6[5:0]};
    wire [12:0] sat7  = {in_7[12],  det_e_second, MANT_MAX};
    wire [12:0] keep7 = {in_7[12],  det_e_second, in_7[5:0]};

    wire [12:0] fix0 = is_sat ? sat0 : keep0;
    wire [12:0] fix1 = is_sat ? sat1 : keep1;
    wire [12:0] fix2 = is_sat ? sat2 : keep2;
    wire [12:0] fix3 = is_sat ? sat3 : keep3;
    wire [12:0] fix4 = is_sat ? sat4 : keep4;
    wire [12:0] fix5 = is_sat ? sat5 : keep5;
    wire [12:0] fix6 = is_sat ? sat6 : keep6;
    wire [12:0] fix7 = is_sat ? sat7 : keep7;

    assign out_0 = (do_repair && det_repair_mask[0] && (is_sat || is_keep)) ? fix0 : in_0;
    assign out_1 = (do_repair && det_repair_mask[1] && (is_sat || is_keep)) ? fix1 : in_1;
    assign out_2 = (do_repair && det_repair_mask[2] && (is_sat || is_keep)) ? fix2 : in_2;
    assign out_3 = (do_repair && det_repair_mask[3] && (is_sat || is_keep)) ? fix3 : in_3;
    assign out_4 = (do_repair && det_repair_mask[4] && (is_sat || is_keep)) ? fix4 : in_4;
    assign out_5 = (do_repair && det_repair_mask[5] && (is_sat || is_keep)) ? fix5 : in_5;
    assign out_6 = (do_repair && det_repair_mask[6] && (is_sat || is_keep)) ? fix6 : in_6;
    assign out_7 = (do_repair && det_repair_mask[7] && (is_sat || is_keep)) ? fix7 : in_7;

    assign repair_applied = do_repair && (is_sat || is_keep);
    assign repair_count   = repair_applied ? 4'd1 : 4'd0;

    wire _unused = |det_argmax_idx;

endmodule
