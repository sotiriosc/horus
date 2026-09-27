`timescale 1ns / 1ps
// tb/tb_scaling_mac.v — Track B4: per-width MAC golden replay.
//
// Compile with -DACC_W=32|34|36 and matching golden filenames.

`ifndef ACC_W
`define ACC_W 32
`endif

module tb_scaling_mac;

    `ifdef ACC_W32
    localparam integer ACC_WIDTH = 32;
    `elsif ACC_W34
    localparam integer ACC_WIDTH = 34;
    `elsif ACC_W36
    localparam integer ACC_WIDTH = 36;
    `else
    localparam integer ACC_WIDTH = 32;
    `endif
    localparam integer HEX_DIGITS = (ACC_WIDTH + 3) / 4;

    reg clk = 0;
    always #5 clk = ~clk;

    reg  [9:0] a, b;
    reg        clear, acc_en, rst;
    wire       prod_sign;
    wire [13:0] prod_P;
    wire [3:0]  prod_w;

    integer prod_pass, prod_fail;
    integer acc_pass, acc_fail;
    integer fd, ret;
    reg [1023:0] line;
    reg [63:0] va, vb, vs, vp, vw, vacc;
    reg [255:0] prod_file, acc_file;

    `ifdef ACC_W32
    wire signed [31:0] acc;
    horus_e3m6_mac_w32 dut (
        .clk(clk), .rst(rst), .a(a), .b(b),
        .clear(clear), .acc_en(acc_en),
        .prod_sign(prod_sign), .prod_P(prod_P), .prod_w(prod_w),
        .acc(acc)
    );
    `elsif ACC_W34
    wire signed [33:0] acc;
    horus_e3m6_mac_w34 dut (
        .clk(clk), .rst(rst), .a(a), .b(b),
        .clear(clear), .acc_en(acc_en),
        .prod_sign(prod_sign), .prod_P(prod_P), .prod_w(prod_w),
        .acc(acc)
    );
    `elsif ACC_W36
    wire signed [35:0] acc;
    horus_e3m6_mac_w36 dut (
        .clk(clk), .rst(rst), .a(a), .b(b),
        .clear(clear), .acc_en(acc_en),
        .prod_sign(prod_sign), .prod_P(prod_P), .prod_w(prod_w),
        .acc(acc)
    );
    `else
    initial begin $display("FAIL: define ACC_W32, ACC_W34, or ACC_W36"); $finish; end
    `endif

    task drive_product;
        input [9:0] ai, bi;
        begin
            a = ai; b = bi;
            clear = 0; acc_en = 0;
            @(posedge clk);
            #1;
        end
    endtask

    function signed [ACC_WIDTH-1:0] sign_extend_acc;
        input [63:0] raw;
        reg signed [ACC_WIDTH-1:0] v;
        begin
            v = raw[ACC_WIDTH-1:0];
            sign_extend_acc = v;
        end
    endfunction

    initial begin
        prod_pass = 0; prod_fail = 0;
        acc_pass = 0; acc_fail = 0;
        rst = 1; clear = 0; acc_en = 0;
        @(posedge clk);
        rst = 0;

        $sformat(prod_file, "SCALING_MAC_PRODUCT_W%0d.hex", ACC_WIDTH);
        $sformat(acc_file, "SCALING_MAC_ACC_GOLDEN_W%0d.hex", ACC_WIDTH);

        fd = $fopen(prod_file, "r");
        if (fd == 0) begin
            $display("FAIL: %s not found", prod_file);
            $finish;
        end
        while (!$feof(fd)) begin
            ret = $fgets(line, fd);
            if (ret != 0) begin
                ret = $sscanf(line, "%h %h %h %h %h", va, vb, vs, vp, vw);
                if (ret == 5) begin
                    drive_product(va[9:0], vb[9:0]);
                    if (prod_sign === vs[0] && prod_P === vp[13:0] && prod_w === vw[3:0])
                        prod_pass = prod_pass + 1;
                    else
                        prod_fail = prod_fail + 1;
                end
            end
        end
        $fclose(fd);

        fd = $fopen(acc_file, "r");
        if (fd == 0) begin
            $display("FAIL: %s not found", acc_file);
            $finish;
        end
        a = 10'd0; b = 10'd0;
        while (!$feof(fd)) begin
            ret = $fgets(line, fd);
            if (ret != 0) begin
                if (line[0] == "/" || line[0] == 8'h0a || line[0] == 8'h0d)
                    ;
                else if ($sscanf(line, "C %h", vacc) == 1) begin
                    clear = 1; acc_en = 0;
                    @(posedge clk);
                    clear = 0;
                    #1;
                end else if ($sscanf(line, "T %h %h", va, vb) == 2) begin
                    a = va[9:0]; b = vb[9:0];
                    clear = 0; acc_en = 1;
                    @(posedge clk);
                    acc_en = 0;
                    #1;
                end else if ($sscanf(line, "A %h", vacc) == 1) begin
                    if (acc === sign_extend_acc(vacc))
                        acc_pass = acc_pass + 1;
                    else begin
                        acc_fail = acc_fail + 1;
                        if (acc_fail <= 5)
                            $display("ACC FAIL W%0d: got=%0d want=%0d",
                                     ACC_WIDTH, acc, sign_extend_acc(vacc));
                    end
                end
            end
        end
        $fclose(fd);

        $display("W%0d products: %0d pass %0d fail", ACC_WIDTH, prod_pass, prod_fail);
        $display("W%0d accumulate: %0d pass %0d fail", ACC_WIDTH, acc_pass, acc_fail);
        if (prod_fail == 0 && acc_fail == 0 && acc_pass > 0)
            $display("PASS  tb_scaling_mac W%0d", ACC_WIDTH);
        else
            $display("FAIL  tb_scaling_mac W%0d", ACC_WIDTH);
        $finish;
    end

endmodule
