`timescale 1ns/1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
module tb_gate_edges;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,source_valid=0,proposal_valid=0,proposal_slot=0;
 reg [15:0] source_id=1,source_record_id=101,proposal_id=1,proposal_record_id=101;
 reg [7:0] source_epoch=1,proposal_epoch=1;
 reg [103:0] source_words={8{13'd656}},proposal_words={8{13'd2064}};
 reg [5:0] source_target=32,source_threshold=13,proposal_scale=10;
 reg [1:0] source_mode=2,proposal_retries=0;
 reg proposal_fault=0;reg [2:0] proposal_lane=0,trace_address=0;
 reg checker_pause=0,sink_ready=0;
 wire source_ready,source_slot,sink_valid,halted,decision_valid;
 wire [103:0] sink_words;wire [15:0] sink_id;wire [7:0] sink_epoch;
 wire [1:0] occupancy,quarantine_occupancy;
 wire [95:0] decision_trace,trace_data;
 commit_gate gate(.*);
 integer sink_count=0,cycles=0,i;
 always @(posedge clk) begin
  cycles=cycles+1;if(cycles>1000)$fatal(1,"edge suite timeout");
  if(rst_n && sink_valid && sink_ready)sink_count=sink_count+1;
 end
 task reset_gate;
 begin
  @(negedge clk);rst_n=0;source_valid=0;proposal_valid=0;
  checker_pause=0;sink_ready=0;
  repeat(2)@(negedge clk);rst_n=1;sink_count=0;
 end endtask
 task capture;
 begin
  @(negedge clk);source_valid=1;
  @(negedge clk);source_valid=0;
 end endtask
 task propose;
 begin
  @(negedge clk);proposal_valid=1;
  @(negedge clk);proposal_valid=0;
 end endtask
 task wait_timeout;
 begin
  i=0;
  while(!decision_valid && i<70)begin @(posedge clk);#1;i=i+1;end
  if(!decision_valid || !decision_trace[8] || !decision_trace[9] ||
     decision_trace[10] || sink_count || !halted) $fatal(1,"timeout did not reject");
  @(negedge clk);
  if(source_ready || sink_valid)$fatal(1,"timeout did not fail-stop");
 end endtask
 initial begin
  // One slot, good proposal, duplicate attempt cannot overwrite it or accept twice.
  reset_gate;capture;propose;
  proposal_words=0;propose;proposal_words={8{13'd2064}};
  @(negedge clk);sink_ready=1;
  @(posedge clk);#1;
  if(!decision_valid || !decision_trace[10] || sink_count!=1) $fatal(1,"good slot lost");
  repeat(3)@(negedge clk);
  if(sink_count!=1 || occupancy!=0)$fatal(1,"duplicate acceptance");
  // A proposal is not authority while the checker has not completed.
  reset_gate;checker_pause=1;capture;propose;sink_ready=1;
  repeat(4)begin @(negedge clk);if(sink_valid)$fatal(1,"bypass while checker paused");end
  checker_pause=0;@(posedge clk);#1;
  if(sink_count!=1 || !decision_trace[10])$fatal(1,"delayed verification failed");
  // Missing proposal and late arrival cannot be silently reassigned.
  reset_gate;capture;wait_timeout;propose;
  repeat(3)@(negedge clk);
  if(sink_count || occupancy!=0 || source_ready)$fatal(1,"late proposal escaped timeout");
  // Checker never completes; bounded rejection.
  reset_gate;checker_pause=1;capture;propose;sink_ready=1;wait_timeout;
  // Sink never ready; bounded rejection rather than unbounded retention.
  reset_gate;capture;propose;wait_timeout;
  // Reset flushes pending state. Trusted source must use a fresh epoch on restart.
  reset_gate;capture;reset_gate;source_epoch=2;proposal_epoch=1;
  capture;propose;sink_ready=1;@(posedge clk);#1;
  if(sink_count || !decision_valid || !decision_trace[9] || decision_trace[16])
    $fatal(1,"stale epoch accepted after restart");
  $display("EDGES PASS duplicate, checker stall, missing/late proposal, checker timeout, sink timeout, restart epoch");
  $finish;
 end
endmodule
