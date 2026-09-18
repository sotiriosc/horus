// SPDX-License-Identifier: CERN-OHL-S-2.0
// Experimental integration. Fault ports are test controls, not production inputs.
module bounded_commit_top #(parameter TRACE_BITS = 96) (
 input wire clk,rst_n,valid_in,
 output wire ready_in,
 input wire [103:0] source_words,
 input wire [15:0] transaction_id,source_record_id,
 input wire [7:0] epoch,
 input wire [2:0] fault_mode,
 input wire [3:0] fault_pattern,
 input wire sink_ready,checker_pause,
 output wire sink_valid,
 output wire [103:0] sink_words,
 output wire [15:0] sink_id,
 output wire [7:0] sink_epoch,
 output wire [1:0] occupancy,quarantine_occupancy,
 output wire halted,decision_valid,
 output wire [95:0] decision_trace,
 input wire [2:0] trace_address,
 output wire [95:0] trace_data,
 output wire proposal_seen,detected,replayed,wrong_accept,
 output wire [103:0] wrong_words
);
 wire evidence_ready,slot,busy,commit_valid,det_valid,det_flag,replay_pulse;
 wire [2:0] det_lane;
 wire [5:0] commit_scale;
 wire [103:0] committed;
 reg active,held_slot,seen_fault,launch;
 reg [103:0] input_words;
 reg [15:0] held_id,held_record;
 reg [7:0] held_epoch;
 reg [2:0] held_mode,seen_lane;
 reg [3:0] held_pattern;
 reg [1:0] retry_count;
 // Reserve protected evidence before the DUT captures the independently faulted copy.
 assign ready_in=evidence_ready && !active && !busy;
 wire fire=valid_in && ready_in;
 reg [103:0] faulted;
 integer fault_lane;
 always @* begin
  faulted=input_words;
  if(held_mode!=0) begin
   case(held_pattern)
    1: faulted[51]=!input_words[51]; // lane 3 sign
    2: faulted[39]=!input_words[39]; // lane 3 mantissa LSB
    3: begin faulted[45 +: 6]=40;faulted[32 +: 6]=40;end // tied maxima
    4: faulted[45 +: 6]=0; // downward exponent corruption
    5: for(fault_lane=0;fault_lane<8;fault_lane=fault_lane+1)
        faulted[fault_lane*13+6 +: 6]=40; // block-wide scale shift
    6: begin faulted[45 +: 6]=40;faulted[58 +: 6]=39;end // near-max pair
    7: begin faulted[45 +: 6]=40;faulted[39]=!input_words[39];end
    8: faulted[45 +: 6]=40; // post-repair sign corruption follows below
    default: faulted[45 +: 6]=40;
   endcase
  end
 end
 wire [103:0] candidate = (held_mode == 2 || held_mode == 5) ?
                         committed ^ 104'd1 :
                         (held_mode!=0 && held_pattern==8) ? committed ^ (104'd1<<12) : committed;
 wire [15:0] candidate_id = held_mode == 3 ? held_id ^ 16'd1 : held_id;
 wire [7:0] candidate_epoch = held_mode == 4 ? held_epoch - 1'b1 : held_epoch;
 wire [15:0] candidate_record = held_mode == 6 ? held_record ^ 16'd1 : held_record;
 // Mode 7 suppresses a proposal to test bounded timeout, outside the main five controls.
 wire present=commit_valid && active && held_mode != 7;
 assign proposal_seen=present;
 // Deliberately WRONG shadow architecture, never connected to the real sink.
 descendant_control wrong_checker(.available(present && held_mode == 5),
   .candidate(candidate),.descendant_reference(candidate),.accept(wrong_accept));
 assign wrong_words=candidate;
 assign detected=det_valid && det_flag;
 assign replayed=replay_pulse;
 always @(posedge clk) begin
  if(!rst_n) begin
   active<=0;launch<=0;input_words<=0;held_slot<=0;held_id<=0;held_record<=0;held_epoch<=0;held_mode<=0;held_pattern<=0;
   seen_fault<=0;seen_lane<=0;retry_count<=0;
  end else begin
   launch<=fire;
   if(fire) begin
    active<=1;input_words<=source_words;held_slot<=slot;held_id<=transaction_id;held_record<=source_record_id;
    held_epoch<=epoch;held_mode<=fault_mode;held_pattern<=fault_pattern;seen_fault<=0;seen_lane<=0;retry_count<=0;
   end
   if(det_valid && det_flag && active) begin seen_fault<=1;seen_lane<=det_lane;end
   if(replay_pulse && active && retry_count<1) retry_count<=retry_count+1'b1;
   if(commit_valid && active) active<=0;
  end
 end
 horus_block_skpr_repair dut (
  .clk(clk),.rst_n(rst_n),.valid_in(launch),
  .in_0(faulted[0 +: 13]),
  .in_1(faulted[13 +: 13]),
  .in_2(faulted[26 +: 13]),
  .in_3(faulted[39 +: 13]),
  .in_4(faulted[52 +: 13]),
  .in_5(faulted[65 +: 13]),
  .in_6(faulted[78 +: 13]),
  .in_7(faulted[91 +: 13]),
  .t_we(1'b1),.t_in(6'd13),.repair_mode(2'd2),
  .persist_bound_q(14'd512),.guard_margin_q(14'd256),
  .commit_valid(commit_valid),.commit_e_max(commit_scale),
  .commit_0(committed[0 +: 13]),
  .commit_1(committed[13 +: 13]),
  .commit_2(committed[26 +: 13]),
  .commit_3(committed[39 +: 13]),
  .commit_4(committed[52 +: 13]),
  .commit_5(committed[65 +: 13]),
  .commit_6(committed[78 +: 13]),
  .commit_7(committed[91 +: 13]),
  .det_valid(det_valid),.det_flag(det_flag),.det_argmax(det_lane),
  .replay_pulse(replay_pulse),.busy(busy)
 );
 commit_gate #(.TRACE_BITS(TRACE_BITS)) gate (
  .clk(clk),.rst_n(rst_n),.source_valid(fire),.source_ready(evidence_ready),.source_slot(slot),
  .source_id(transaction_id),.source_epoch(epoch),.source_record_id(source_record_id),
  .source_words(source_words),.source_target(6'd32),.source_threshold(6'd13),.source_mode(2'd2),
  .proposal_valid(present),.proposal_slot(held_slot),.proposal_id(candidate_id),
  .proposal_epoch(candidate_epoch),.proposal_record_id(candidate_record),
  .proposal_words(candidate),.proposal_scale(commit_scale),.proposal_fault(seen_fault),
  .proposal_lane(seen_lane),.proposal_retries(retry_count),
  .checker_pause(checker_pause),.sink_ready(sink_ready),.sink_valid(sink_valid),
  .sink_words(sink_words),.sink_id(sink_id),.sink_epoch(sink_epoch),
  .occupancy(occupancy),.quarantine_occupancy(quarantine_occupancy),.halted(halted),
  .decision_valid(decision_valid),.decision_trace(decision_trace),
  .trace_address(trace_address),.trace_data(trace_data)
 );
endmodule
