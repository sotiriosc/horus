// SPDX-License-Identifier: CERN-OHL-S-2.0
// ============================================================================
// tb_skpr.v — SKPR RTL co-simulation testbench
//
// Reads a stimulus text file, drives the DUT, writes response text file.
// Invocation:
//   vvp sim/tb_skpr.vvp \
//       +SKPR_STIM=<path> \
//       +SKPR_RESP=<path>
//
// Stimulus format (text, one value per line):
//   Line 0 : persist_bound_q (integer)
//   Line 1 : guard_margin_q  (integer)
//   Line 2 : n_blocks        (integer)
//   Lines 3..(3+n_blocks-1) : e_max value per block (0..63)
//
// Response format (text, one line per block):
//   state_exp ceiling_exp tag event event_dir
//   (all decimal integers; event and event_dir are 0/1)
//
// DUT has 1-cycle registered outputs.  Output on cycle N reflects the
// block driven on cycle N.  This testbench captures state_exp_out etc.
// immediately after the rising edge (registered values are stable).
//
// AI role: compilation and adversarial review (Claude/Anthropic).
// Architectural decisions: Sotirios Chortogiannos.
// ============================================================================

`timescale 1ns / 1ps

module tb_skpr;

    localparam MAX_BLOCKS = 200_000;

    // ── Clock and reset ────────────────────────────────────────────────────────
    reg clk   = 0;
    reg rst_n = 0;
    always #5 clk = ~clk;   // 100 MHz

    // ── DUT ports ─────────────────────────────────────────────────────────────
    reg        valid_in  = 0;
    reg  [5:0] e_max_in  = 0;
    reg [13:0] pbq       = 0;
    reg [13:0] gmq       = 0;

    wire [5:0] state_exp_out;
    wire [5:0] ceiling_exp_out;
    wire [1:0] tag_out;
    wire       event_valid_out;
    wire       event_dir_out;

    skpr #(
        .K          (3'd4),
        .N_SETTLE   (3'd4),
        .ALPHA_SHIFT(4'd4)
    ) dut (
        .clk             (clk),
        .rst_n           (rst_n),
        .valid_in        (valid_in),
        .e_max_in        (e_max_in),
        .persist_bound_q (pbq),
        .guard_margin_q  (gmq),
        .state_exp_out   (state_exp_out),
        .ceiling_exp_out (ceiling_exp_out),
        .tag_out         (tag_out),
        .event_valid_out (event_valid_out),
        .event_dir_out   (event_dir_out)
    );

    // ── Stream storage ─────────────────────────────────────────────────────────
    integer stream [0:MAX_BLOCKS-1];

    // ── File handles and loop vars ─────────────────────────────────────────────
    integer stim_fd, resp_fd;
    integer n_blocks;
    integer i, tmp;

    // Plusargs paths (packed string; 512 bits = 64 chars per path)
    reg [511:0] stim_path, resp_path;

    // H-HW2 assertion state
    integer prev_state_exp;
    integer assertion_failures;
    integer reseed_count;

    // ── Main ──────────────────────────────────────────────────────────────────
    initial begin
        assertion_failures = 0;
        reseed_count       = 0;
        prev_state_exp     = 0;

        // ── Get file paths ────────────────────────────────────────────────────
        if (!$value$plusargs("SKPR_STIM=%s", stim_path)) begin
            $display("ERROR: +SKPR_STIM=<path> required");
            $finish;
        end
        if (!$value$plusargs("SKPR_RESP=%s", resp_path)) begin
            $display("ERROR: +SKPR_RESP=<path> required");
            $finish;
        end

        // ── Open and read stimulus ────────────────────────────────────────────
        stim_fd = $fopen(stim_path, "r");
        if (stim_fd == 0) begin
            $display("ERROR: cannot open SKPR_STIM"); $finish;
        end
        $fscanf(stim_fd, "%d\n", tmp); pbq      = tmp[13:0];
        $fscanf(stim_fd, "%d\n", tmp); gmq      = tmp[13:0];
        $fscanf(stim_fd, "%d\n", n_blocks);
        for (i = 0; i < n_blocks; i = i + 1)
            $fscanf(stim_fd, "%d\n", stream[i]);
        $fclose(stim_fd);

        // ── Open response file ────────────────────────────────────────────────
        resp_fd = $fopen(resp_path, "w");
        if (resp_fd == 0) begin
            $display("ERROR: cannot open SKPR_RESP"); $finish;
        end

        // ── Reset DUT ─────────────────────────────────────────────────────────
        rst_n = 0;
        @(posedge clk); #1;
        @(posedge clk); #1;
        rst_n = 1;
        @(posedge clk); #1;   // first post-reset cycle: outputs=0

        // ── Drive blocks and capture outputs ──────────────────────────────────
        for (i = 0; i < n_blocks; i = i + 1) begin
            e_max_in = stream[i][5:0];
            valid_in = 1;
            @(posedge clk); #1;
            // Outputs now stable (registered by posedge above)

            // H-HW2(a) in-band assertion: OUTLIER tag → no state change
            if (tag_out == 2'b01) begin
                if (state_exp_out != prev_state_exp[5:0]) begin
                    $display("H-HW2(a) FAIL block %0d: OUTLIER but state_exp changed %0d->%0d",
                             i, prev_state_exp, state_exp_out);
                    assertion_failures = assertion_failures + 1;
                end
            end
            prev_state_exp = state_exp_out;

            if (event_valid_out) reseed_count = reseed_count + 1;

            // Write response
            $fdisplay(resp_fd, "%0d %0d %0d %0d %0d",
                state_exp_out, ceiling_exp_out, tag_out,
                event_valid_out, event_dir_out);
        end

        valid_in = 0;
        $fclose(resp_fd);

        if (assertion_failures > 0)
            $display("H-HW2(a) assertions: %0d FAILURES", assertion_failures);
        else
            $display("H-HW2(a) assertions: PASS (no state change on OUTLIER blocks)");
        $display("Total re-seed events: %0d", reseed_count);
        $finish;
    end

    // ── Timeout guard ─────────────────────────────────────────────────────────
    initial begin
        #500_000_000;
        $display("TIMEOUT");
        $finish;
    end

endmodule
