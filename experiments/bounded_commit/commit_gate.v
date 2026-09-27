// SPDX-License-Identifier: CERN-OHL-S-2.0
// Two reserved slots: protected evidence and quarantine are distinct banks.
// An available proposal is never sufficient to authorize a sink transfer.
module commit_gate #(parameter KEEP_TRACE = 1, parameter TRACE_BITS = 96) (
 input wire clk, rst_n,
 input wire source_valid,
 output wire source_ready,
 output wire source_slot,
 input wire [15:0] source_id, source_record_id,
 input wire [7:0] source_epoch,
 input wire [103:0] source_words,
 input wire [5:0] source_target, source_threshold,
 input wire [1:0] source_mode,
 input wire proposal_valid, proposal_slot,
 input wire [15:0] proposal_id, proposal_record_id,
 input wire [7:0] proposal_epoch,
 input wire [103:0] proposal_words,
 input wire [5:0] proposal_scale,
 input wire proposal_fault,
 input wire [2:0] proposal_lane,
 input wire [1:0] proposal_retries,
 input wire checker_pause, sink_ready,
 output wire sink_valid,
 output wire [103:0] sink_words,
 output wire [15:0] sink_id,
 output wire [7:0] sink_epoch,
 output wire [1:0] occupancy, quarantine_occupancy,
 output reg halted,
 output reg decision_valid,
 output reg [95:0] decision_trace,
 input wire [2:0] trace_address,
 output wire [95:0] trace_data
);
 localparam integer DEADLINE = 63;
 reg [15:0] evid_id[0:1], evid_rid[0:1];
 reg [7:0] evid_epoch[0:1];
 reg [103:0] evid_words[0:1];
 reg [5:0] evid_target[0:1], evid_threshold[0:1];
 reg [1:0] evid_mode[0:1];
 reg [15:0] cand_id[0:1], cand_rid[0:1];
 reg [7:0] cand_epoch[0:1];
 reg [103:0] cand_words[0:1];
 reg [5:0] cand_scale[0:1];
 reg fault[0:1]; reg [2:0] lane[0:1]; reg [1:0] retries[0:1];
 reg valid[0:1], arrived[0:1]; reg [5:0] age[0:1];
 reg head, tail; reg [1:0] count;
 reg [TRACE_BITS-1:0] trace[0:7]; reg [2:0] trace_next;
 wire domain_ok, numerical_ok;
 wire [103:0] expected_words;
 independent_spec u_spec(evid_words[head], evid_target[head],
   evid_threshold[head], evid_mode[head], cand_words[head], cand_scale[head],
   domain_ok, expected_words, numerical_ok);
 wire id_ok = cand_id[head] == evid_id[head];
 wire epoch_ok = cand_epoch[head] == evid_epoch[head];
 wire record_ok = cand_rid[head] == evid_rid[head];
 wire identity_ok = id_ok && epoch_ok && record_ok;
 wire expired = valid[head] && age[head] == DEADLINE;
 wire checked = valid[head] && arrived[head] && !checker_pause && !halted;
 wire authorized = checked && identity_ok && numerical_ok && !expired;
 assign sink_valid = authorized;
 assign sink_words = cand_words[head];
 assign sink_id = cand_id[head]; assign sink_epoch = cand_epoch[head];
 wire accepted = sink_valid && sink_ready;
 wire rejected = valid[head] && (expired || (checked && (!identity_ok || !numerical_ok)));
 wire finish = accepted || rejected;
 assign source_ready = count < 2 && !halted;
 assign source_slot = tail;
 wire capture = source_valid && source_ready;
 assign occupancy = count;
 assign quarantine_occupancy = {1'b0,arrived[0]} + {1'b0,arrived[1]};
 assign trace_data = trace[trace_address];
 // Trace layout documented in README: 33 reserved bits, then identity/status.
 wire [95:0] record = {33'd0, evid_id[head], evid_epoch[head], evid_rid[head],
   fault[head], lane[head], arrived[head],
   (checked && id_ok), (checked && epoch_ok), (checked && record_ok),
   (checked && numerical_ok), authorized, retries[head], accepted, rejected,
   expired, {2'b0,age[head]}};
 integer i;
 always @(posedge clk) begin
  if (!rst_n) begin
   head<=0;tail<=0;count<=0;halted<=0;decision_valid<=0;decision_trace<=0;trace_next<=0;
   for(i=0;i<2;i=i+1) begin
    valid[i]<=0;arrived[i]<=0;age[i]<=0;
    evid_id[i]<=0;evid_rid[i]<=0;evid_epoch[i]<=0;evid_words[i]<=0;
    evid_target[i]<=0;evid_threshold[i]<=0;evid_mode[i]<=0;
    cand_id[i]<=0;cand_rid[i]<=0;cand_epoch[i]<=0;cand_words[i]<=0;cand_scale[i]<=0;
    fault[i]<=0;lane[i]<=0;retries[i]<=0;
   end
   for(i=0;i<8;i=i+1) trace[i]<=0;
  end else begin
   decision_valid<=0;
   for(i=0;i<2;i=i+1)
    if(valid[i] && age[i]<DEADLINE) age[i]<=age[i]+1'b1;
   if(capture) begin
    valid[tail]<=1;arrived[tail]<=0;age[tail]<=0;
    evid_id[tail]<=source_id;evid_epoch[tail]<=source_epoch;evid_rid[tail]<=source_record_id;
    evid_words[tail]<=source_words;evid_target[tail]<=source_target;
    evid_threshold[tail]<=source_threshold;evid_mode[tail]<=source_mode;
    fault[tail]<=0;lane[tail]<=0;retries[tail]<=0;
    tail<=!tail;
   end
   // Duplicate proposals cannot overwrite a pending slot. Timeout is fail-stop:
   // no late output may be associated with a newly reused slot until reset.
   if(proposal_valid && valid[proposal_slot] && !arrived[proposal_slot] && !halted) begin
    arrived[proposal_slot]<=1;
    cand_id[proposal_slot]<=proposal_id;cand_epoch[proposal_slot]<=proposal_epoch;
    cand_rid[proposal_slot]<=proposal_record_id;cand_words[proposal_slot]<=proposal_words;
    cand_scale[proposal_slot]<=proposal_scale;
    fault[proposal_slot]<=proposal_fault;lane[proposal_slot]<=proposal_lane;
    retries[proposal_slot]<=proposal_retries;
   end
   if(finish) begin
    decision_valid<=1;decision_trace<=record;
    if(KEEP_TRACE) begin trace[trace_next]<=record;trace_next<=trace_next+1'b1;end
    valid[head]<=0;arrived[head]<=0;head<=!head;
    if(expired) halted<=1;
   end
   case({capture,finish})
    2'b10: count<=count+1'b1;
    2'b01: count<=count-1'b1;
    default: count<=count;
   endcase
  end
 end
endmodule
