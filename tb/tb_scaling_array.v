`timescale 1ns / 1ps
// tb/tb_scaling_array.v — Track C3 smoke test (wiring harness only).

`ifndef ARRAY_TOP
`define ARRAY_TOP 2x2
`endif

module tb_scaling_array;

    reg clk = 0;
    always #5 clk = ~clk;

    reg        rst_n;
    reg        mode;
    reg [9:0]  op_a [0:15];
    reg [9:0]  op_b [0:15];
    wire [12:0] nfe_out [0:15];

    integer i, fd, ret, fails, checks;
    reg [1023:0] line;
    reg [31:0] m, oa, ob, exp, got;

    `ifdef ARRAY_2X2
    horus_array_2x2 dut (
        .clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a_00(op_a[0]),  .op_b_00(op_b[0]),  .nfe_out_00(nfe_out[0]),
        .op_a_01(op_a[1]),  .op_b_01(op_b[1]),  .nfe_out_01(nfe_out[1]),
        .op_a_10(op_a[2]),  .op_b_10(op_b[2]),  .nfe_out_10(nfe_out[2]),
        .op_a_11(op_a[3]),  .op_b_11(op_b[3]),  .nfe_out_11(nfe_out[3])
    );
    localparam integer NTILES = 4;
    `elsif ARRAY_4X4
    horus_array_4x4 dut (
        .clk(clk), .rst_n(rst_n), .mode(mode),
        .op_a_00(op_a[0]),  .op_b_00(op_b[0]),  .nfe_out_00(nfe_out[0]),
        .op_a_01(op_a[1]),  .op_b_01(op_b[1]),  .nfe_out_01(nfe_out[1]),
        .op_a_02(op_a[2]),  .op_b_02(op_b[2]),  .nfe_out_02(nfe_out[2]),
        .op_a_03(op_a[3]),  .op_b_03(op_b[3]),  .nfe_out_03(nfe_out[3]),
        .op_a_10(op_a[4]),  .op_b_10(op_b[4]),  .nfe_out_10(nfe_out[4]),
        .op_a_11(op_a[5]),  .op_b_11(op_b[5]),  .nfe_out_11(nfe_out[5]),
        .op_a_12(op_a[6]),  .op_b_12(op_b[6]),  .nfe_out_12(nfe_out[6]),
        .op_a_13(op_a[7]),  .op_b_13(op_b[7]),  .nfe_out_13(nfe_out[7]),
        .op_a_20(op_a[8]),  .op_b_20(op_b[8]),  .nfe_out_20(nfe_out[8]),
        .op_a_21(op_a[9]),  .op_b_21(op_b[9]),  .nfe_out_21(nfe_out[9]),
        .op_a_22(op_a[10]), .op_b_22(op_b[10]), .nfe_out_22(nfe_out[10]),
        .op_a_23(op_a[11]), .op_b_23(op_b[11]), .nfe_out_23(nfe_out[11]),
        .op_a_30(op_a[12]), .op_b_30(op_b[12]), .nfe_out_30(nfe_out[12]),
        .op_a_31(op_a[13]), .op_b_31(op_b[13]), .nfe_out_31(nfe_out[13]),
        .op_a_32(op_a[14]), .op_b_32(op_b[14]), .nfe_out_32(nfe_out[14]),
        .op_a_33(op_a[15]), .op_b_33(op_b[15]), .nfe_out_33(nfe_out[15])
    );
    localparam integer NTILES = 16;
    `else
    initial begin $display("FAIL: define ARRAY_2X2 or ARRAY_4X4"); $finish; end
    `endif

    initial begin
        fails = 0; checks = 0;
        rst_n = 0; mode = 0;
        for (i = 0; i < 16; i = i + 1) begin op_a[i] = 0; op_b[i] = 0; end
        repeat (3) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        for (i = 0; i < NTILES; i = i + 1)
            if (nfe_out[i] === 13'bx)
                fails = fails + 1;

        fd = $fopen("SCALING_ARRAY_SMOKE.hex", "r");
        if (fd == 0) begin
            $display("FAIL: SCALING_ARRAY_SMOKE.hex missing");
            $finish;
        end
        i = 0;
        while (!$feof(fd) && i < NTILES) begin
            ret = $fgets(line, fd);
            if (ret != 0) begin
                ret = $sscanf(line, "%d %h %h %h", m, oa, ob, exp);
                if (ret == 4) begin
                    mode = m[0];
                    op_a[i] = oa[9:0];
                    op_b[i] = ob[9:0];
                    @(posedge clk);
                    #1;
                    got = nfe_out[i];
                    checks = checks + 1;
                    if (got[12:0] !== exp[12:0]) begin
                        fails = fails + 1;
                        $display("FAIL tile %0d: got=%04x want=%04x", i, got[12:0], exp[12:0]);
                    end
                    i = i + 1;
                end
            end
        end
        $fclose(fd);

        if (fails == 0 && checks == NTILES)
            $display("PASS  tb_scaling_array (%0d tiles, %0d checks)", NTILES, checks);
        else
            $display("FAIL  tb_scaling_array fails=%0d checks=%0d", fails, checks);
        $finish;
    end

endmodule
