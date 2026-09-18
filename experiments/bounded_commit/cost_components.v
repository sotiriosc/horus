// SPDX-License-Identifier: CERN-OHL-S-2.0
// Synthesis probes ONLY: standalone estimates, not additive attribution after
// whole-gate optimization. Same depth, reset, write and read shape as gate banks.
module evidence_bank(input wire clk,rst_n,we,wr,rd,
 input wire [157:0] d,output wire [157:0] q);
 reg [157:0] words[0:1];
 always @(posedge clk)begin
  if(!rst_n)begin words[0]<=0;words[1]<=0;end
  else if(we)words[wr]<=d;
 end
 assign q=words[rd];
endmodule
module quarantine_bank(input wire clk,rst_n,we,wr,rd,
 input wire [155:0] d,output wire [155:0] q);
 reg [155:0] words[0:1];
 always @(posedge clk)begin
  if(!rst_n)begin words[0]<=0;words[1]<=0;end
  else if(we)words[wr]<=d;
 end
 assign q=words[rd];
endmodule
module identity_comparators(input wire [39:0] protected_tuple,candidate_tuple,
 output wire id_ok,epoch_ok,record_ok);
 assign id_ok=protected_tuple[39:24]==candidate_tuple[39:24];
 assign epoch_ok=protected_tuple[23:16]==candidate_tuple[23:16];
 assign record_ok=protected_tuple[15:0]==candidate_tuple[15:0];
endmodule
