`timescale 1ns / 1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// tb_skpr_block_detect.v — Rule 5 detect-only vs skpr_golden vectors
// Plusarg: +VECTORS=skpr_vectors.txt  (space-separated twin from skpr_golden.py)
// ============================================================================

module tb_skpr_block_detect;
    localparam CLK_HALF = 5;

    reg clk = 0;
    always #CLK_HALF clk = ~clk;

    reg rst_n, valid_in, t_we;
    reg [5:0] t_in;
    reg [12:0] in_0, in_1, in_2, in_3, in_4, in_5, in_6, in_7;

    wire valid_out, flag_out;
    wire [5:0] e_max_out, e_second_out, gap_out;

    skpr_block_detect dut (
        .clk(clk), .rst_n(rst_n), .valid_in(valid_in),
        .in_0(in_0), .in_1(in_1), .in_2(in_2), .in_3(in_3),
        .in_4(in_4), .in_5(in_5), .in_6(in_6), .in_7(in_7),
        .t_we(t_we), .t_in(t_in),
        .valid_out(valid_out), .flag_out(flag_out),
        .e_max_out(e_max_out), .e_second_out(e_second_out), .gap_out(gap_out)
    );

    integer fd, code, n_vec, fail, done;
    integer T_vec, flag_sat_i, emaxout_sat_i, e_max_i, e_second_i, gap_i, argmax_sat_i;
    integer flag_keep_i, emaxout_keep_i, argmax_keep_i;
    reg [12:0] vin [0:7];
    reg [12:0] vout_sat [0:7];
    reg [12:0] vout_keep [0:7];
    reg [256*8-1:0] vpath;
    reg [64*8-1:0]  vname;
    integer scale_ok;

    initial begin
        n_vec = 0; fail = 0; done = 0;
        valid_in = 0; t_we = 0; t_in = 0;
        in_0=0; in_1=0; in_2=0; in_3=0;
        in_4=0; in_5=0; in_6=0; in_7=0;
        rst_n = 0;
        repeat (4) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        if (!$value$plusargs("VECTORS=%s", vpath))
            vpath = "skpr_vectors.txt";
        fd = $fopen(vpath, "r");
        if (fd == 0) begin
            $display("ERROR: cannot open %0s", vpath);
            $finish;
        end

        while (!$feof(fd) && !done) begin
            code = $fscanf(fd,
                "%s %d %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %d %d %d %d %d %d %h %h %h %h %h %h %h %h %d %d %d",
                vname, T_vec,
                vin[0],vin[1],vin[2],vin[3],vin[4],vin[5],vin[6],vin[7],
                vout_sat[0],vout_sat[1],vout_sat[2],vout_sat[3],
                vout_sat[4],vout_sat[5],vout_sat[6],vout_sat[7],
                flag_sat_i, emaxout_sat_i, e_max_i, e_second_i, gap_i, argmax_sat_i,
                vout_keep[0],vout_keep[1],vout_keep[2],vout_keep[3],
                vout_keep[4],vout_keep[5],vout_keep[6],vout_keep[7],
                flag_keep_i, emaxout_keep_i, argmax_keep_i
            );
            if (code < 35) begin
                done = 1;
            end else begin
                if (n_vec == 0) begin
                    @(negedge clk); t_we = 1; t_in = T_vec[5:0];
                    @(posedge clk);
                    @(negedge clk); t_we = 0;
                    @(posedge clk);
                end

                @(negedge clk);
                in_0=vin[0]; in_1=vin[1]; in_2=vin[2]; in_3=vin[3];
                in_4=vin[4]; in_5=vin[5]; in_6=vin[6]; in_7=vin[7];
                valid_in = 1;
                @(posedge clk);
                @(negedge clk); valid_in = 0;
                @(posedge clk);
                #1;

                n_vec = n_vec + 1;
                if (flag_out !== flag_sat_i[0] ||
                    e_max_out !== e_max_i[5:0] ||
                    e_second_out !== e_second_i[5:0] ||
                    gap_out !== gap_i[5:0]) begin
                    fail = fail + 1;
                    if (fail <= 5)
                        $display("FAIL %0s flag=%0d/%0d emax=%0d/%0d e2=%0d/%0d gap=%0d/%0d",
                            vname, flag_out, flag_sat_i, e_max_out, e_max_i,
                            e_second_out, e_second_i, gap_out, gap_i);
                end

                // block_scale contract: flag ⇒ e_second else e_max
                scale_ok = flag_out ? (e_second_out === e_second_i[5:0])
                                    : (e_max_out === e_max_i[5:0]);
                if (!scale_ok) begin
                    fail = fail + 1;
                    if (fail <= 5) $display("FAIL scale %0s", vname);
                end
            end
        end
        $fclose(fd);

        $display("============================================================");
        $display("skpr_block_detect vs golden: vectors=%0d fails=%0d", n_vec, fail);
        $display("============================================================");
        if (fail != 0) $fatal(1, "detect sidecar FALSIFIED");
        else $display("DETECT SIDECAR PASS");
        $finish;
    end
endmodule
