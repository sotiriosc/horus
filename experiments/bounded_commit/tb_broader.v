`timescale 1ns/1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
// Follow-up only. Rejection is a successful protection outcome, not repair.
module tb_broader;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,valid_in=0,sink_ready=1,checker_pause=0;
 reg [103:0] source_words={8{13'd656}};
 reg [15:0] transaction_id=1,source_record_id=4097;
 reg [7:0] epoch=1;
 reg [2:0] fault_mode=1,trace_address=0;
 reg [3:0] fault_pattern=0;
 wire ready_in,sink_valid,halted,decision_valid,proposal_seen,detected,replayed,wrong_accept;
 wire [103:0] sink_words,wrong_words;wire [15:0] sink_id;wire [7:0] sink_epoch;
 wire [1:0] occupancy,quarantine_occupancy;wire [95:0] decision_trace,trace_data;
 bounded_commit_top top(.*);
 integer seed,pattern,n,waited,accepted=0,rejected=0,detected_n=0,replayed_n=0,cycles=0;
 reg [31:0] rng;
 always @(posedge clk)if(rst_n)begin
  cycles=cycles+1;if(cycles>20000)$fatal(1,"broader deadline");
  if(sink_valid && sink_ready)begin
   accepted=accepted+1;
   if(sink_words!={8{13'd2064}} || sink_id!=transaction_id || sink_epoch!=seed)
     $fatal(1,"broader false accept");
  end
  if(detected)detected_n=detected_n+1;
  if(replayed)replayed_n=replayed_n+1;
 end
 initial begin
  if(!$value$plusargs("SEED=%d",seed))seed=1;
  if(!$value$plusargs("PATTERN=%d",pattern))pattern=0;
  rng=seed;epoch=seed;fault_pattern=pattern;
  repeat(4)@(negedge clk);rst_n=1;
  for(n=0;n<100;n=n+1)begin
   rng=rng*32'd1664525+32'd1013904223;
   repeat(rng%3)@(negedge clk);
   while(!ready_in)@(negedge clk);
   transaction_id=n+1;source_record_id=n+4097;valid_in=1;
   @(negedge clk);valid_in=0;waited=0;
   while(!decision_valid && waited<65)begin @(posedge clk);#1;waited=waited+1;end
   if(!decision_valid || decision_trace[8])$fatal(1,"broader unexpected timeout");
   if(decision_trace[9])rejected=rejected+1;
   if(decision_trace[10] && (!decision_trace[13] || !(&decision_trace[17:14])))
     $fatal(1,"broader unverified acceptance");
   @(negedge clk);
  end
  // Only original exponent spike is reversible by KEEP in this fixed domain.
  if(accepted!=(pattern==0?100:0) || rejected!=(pattern==0?0:100))
    $fatal(1,"broader control failed");
  $display("BROADER seed=%0d pattern=%0d transactions=100 accepted=%0d rejected=%0d false_accept=0 detected=%0d replayed=%0d",seed,pattern,accepted,rejected,detected_n,replayed_n);
  $display("BROADER PASS");$finish;
 end
endmodule
