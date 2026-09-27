`timescale 1ns / 1ps
// tb/tb_jacobi_mac.v — Phase 4b R1: horus_e3m6_mac vs jacobi_mac_model.py goldens.
//
// (a) Replay all 38,408 operand pairs: full product (sign, P, w) bit-exact.
// (b) Replay accumulation sequences vs JACOBI_MAC_ACC_GOLDEN.hex.
//
// Usage (from sim/):
//   python3 jacobi_mac_model.py
//   iverilog -g2012 -Wall -o sim_jacobi_mac ../tb/tb_jacobi_mac.v ../rtl/horus_e3m6_mac.v
//   vvp sim_jacobi_mac

module tb_jacobi_mac;

    reg clk = 0;
    always #5 clk = ~clk;

    reg  [9:0] a, b;
    reg        clear, acc_en, rst;
    wire       prod_sign;
    wire [13:0] prod_P;
    wire [3:0]  prod_w;
    wire signed [31:0] acc;

    horus_e3m6_mac dut (
        .clk(clk), .rst(rst), .a(a), .b(b),
        .clear(clear), .acc_en(acc_en),
        .prod_sign(prod_sign), .prod_P(prod_P), .prod_w(prod_w),
        .acc(acc)
    );

    integer prod_pass, prod_fail;
    integer acc_pass, acc_fail;
    integer fd, ret;
    reg [1023:0] line;
    reg [31:0] va, vb, vs, vp, vw, vacc;

    task drive_product;
        input [9:0] ai, bi;
        begin
            a = ai; b = bi;
            clear = 0; acc_en = 0;
            @(posedge clk);
            #1;
        end
    endtask

    initial begin
        prod_pass = 0; prod_fail = 0;
        acc_pass = 0; acc_fail = 0;
        rst = 1; clear = 0; acc_en = 0;
        @(posedge clk);
        rst = 0;

        // ── (a) Product replay ────────────────────────────────────────────────
        fd = $fopen("JACOBI_MAC_PRODUCT_GOLDEN.hex", "r");
        if (fd == 0) begin
            $display("FAIL: JACOBI_MAC_PRODUCT_GOLDEN.hex not found");
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
                    else begin
                        prod_fail = prod_fail + 1;
                        if (prod_fail <= 10)
                            $display("PROD FAIL: A=0x%03X B=0x%03X got s=%b P=%04X w=%X want s=%b P=%04X w=%X",
                                     va[9:0], vb[9:0], prod_sign, prod_P, prod_w,
                                     vs[0], vp[13:0], vw[3:0]);
                    end
                end
            end
        end
        $fclose(fd);

        // ── (b) Accumulation replay ───────────────────────────────────────────
        fd = $fopen("JACOBI_MAC_ACC_GOLDEN.hex", "r");
        if (fd == 0) begin
            $display("FAIL: JACOBI_MAC_ACC_GOLDEN.hex not found");
            $finish;
        end
        a = 10'd0; b = 10'd0;
        while (!$feof(fd)) begin
            ret = $fgets(line, fd);
            if (ret != 0) begin
                if (line[0] == "/" || line[0] == 8'h0a || line[0] == 8'h0d)
                    ; // skip comments / blank
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
                    if (acc === $signed(vacc))
                        acc_pass = acc_pass + 1;
                    else begin
                        acc_fail = acc_fail + 1;
                        if (acc_fail <= 10)
                            $display("ACC FAIL: got=%0d want=%0d", acc, $signed(vacc));
                    end
                end
            end
        end
        $fclose(fd);

        $display("");
        $display("MAC product stream: %0d pairs checked.", prod_pass + prod_fail);
        if (prod_fail == 0)
            $display("PASS  products: %0d/%0d bit-exact", prod_pass, prod_pass);
        else
            $display("FAIL  products: %0d mismatches / %0d pairs", prod_fail, prod_pass + prod_fail);

        $display("MAC accumulate stream: %0d acc checks (%0d events).",
                 acc_pass + acc_fail, acc_pass + acc_fail);
        if (acc_fail == 0 && (acc_pass + acc_fail) > 0)
            $display("PASS  accumulate: %0d/%0d bit-exact", acc_pass, acc_pass);
        else if (acc_fail == 0 && (acc_pass + acc_fail) == 0)
            $display("FAIL  accumulate: 0 acc checks replayed");
        else
            $display("FAIL  accumulate: %0d mismatches / %0d acc checks",
                     acc_fail, acc_pass + acc_fail);

        if (prod_fail == 0 && acc_fail == 0 && (acc_pass + acc_fail) > 0)
            $display("PASS  tb_jacobi_mac (R1): %0d/38408 products, 100%% accumulate steps",
                     prod_pass);
        else if (prod_fail == 0)
            $display("FAIL  tb_jacobi_mac (R1): products OK, accumulate replay incomplete");
        else
            $display("FAIL  tb_jacobi_mac (R1)");

        $finish;
    end

endmodule
