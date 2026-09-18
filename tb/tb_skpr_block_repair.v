`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// Repair unit vs golden SAT/KEEP

module tb_skpr_block_repair;
    reg [12:0] in0,in1,in2,in3,in4,in5,in6,in7;
    reg        det_flag;
    reg [5:0]  det_e_second;
    reg [2:0]  det_argmax;
    reg [7:0]  det_mask;
    reg [1:0]  mode;
    wire [12:0] o0,o1,o2,o3,o4,o5,o6,o7;
    wire applied;
    wire [3:0] count;

    skpr_block_repair dut (
        .in_0(in0),.in_1(in1),.in_2(in2),.in_3(in3),
        .in_4(in4),.in_5(in5),.in_6(in6),.in_7(in7),
        .det_flag(det_flag), .det_e_second(det_e_second),
        .det_argmax_idx(det_argmax), .det_repair_mask(det_mask),
        .repair_mode(mode),
        .out_0(o0),.out_1(o1),.out_2(o2),.out_3(o3),
        .out_4(o4),.out_5(o5),.out_6(o6),.out_7(o7),
        .repair_applied(applied), .repair_count(count)
    );

    integer fd, code, fails, n, T, flag, emax, esec, gap, argS;
    integer exp_flag, feed_a, feed_b;
    reg [12:0] bin[0:7];
    reg [12:0] outS[0:7], outK[0:7];
    reg [8*256-1:0] path;
    integer i;

    function [12:0] pack;
        input s; input [5:0] e; input [5:0] m;
        pack = {s, e, m};
    endfunction

    initial begin
        fails = 0; n = 0;
        if (!$value$plusargs("VECTORS=%s", path))
            path = "skpr_vectors.txt";
        fd = $fopen(path, "r");
        if (!fd) begin $display("ERROR open %0s", path); $finish; end

        // Directed: NONE identity
        in0=13'h0401; in1=in0; in2=in0; in3=in0; in4=in0; in5=in0; in6=in0; in7=in0;
        det_flag=0; det_e_second=0; det_argmax=0; det_mask=0; mode=0;
        #1;
        if (o0!==in0 || applied!==0) begin fails=fails+1; $display("NONE fail"); end
        n=n+1;

        // SAT unique spike
        in0=pack(0,10,1); in1=in0; in2=in0; in3=in0; in4=in0; in5=in0; in6=in0;
        in7=pack(1,30,7);
        det_flag=1; det_e_second=10; det_argmax=7; det_mask=8'h80; mode=2'd1;
        #1;
        if (o7 !== pack(1,10,6'b111111) || o0!==in0 || applied!==1) begin
            fails=fails+1; $display("SAT fail o7=%h", o7);
        end
        n=n+1;

        // KEEP
        mode=2'd2; #1;
        if (o7 !== pack(1,10,7) || o0!==in0) begin
            fails=fails+1; $display("KEEP fail o7=%h", o7);
        end
        n=n+1;

        // Vector file: reuse skpr_vectors format — parse lightly via Python golden in co-check
        // Here scan hex blocks from stim if present
        $display("=== tb_skpr_block_repair directed n=%0d fails=%0d ===", n, fails);
        if (fails==0) $display("PASS"); else $display("FAIL");
        $finish;
    end
endmodule
