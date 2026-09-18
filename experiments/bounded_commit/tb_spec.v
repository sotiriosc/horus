`timescale 1ns/1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
module tb_spec;
 reg [103:0] source_words={8{13'd656}},proposed_words={8{13'd2064}};
 reg [5:0] target_exp=32,threshold=13,proposed_scale=10;
 reg [1:0] repair_mode=2;
 wire domain_ok,numerical_ok;wire [103:0] expected_words;
 independent_spec spec(.*);
 integer i;
 initial begin
  #1;if(!numerical_ok || expected_words!={8{13'd2064}}) $fatal(1,"clean known answer");
  // Audit every single-bit wrong result and every single-bit protected input
  // outside this deliberately narrow domain. No imported arithmetic oracle.
  for(i=0;i<104;i=i+1) begin
   proposed_words={8{13'd2064}} ^ (104'd1<<i);
   #1;if(numerical_ok) $fatal(1,"wrong output bit %0d accepted",i);
  end
  proposed_words={8{13'd2064}};
  for(i=0;i<104;i=i+1) begin
   source_words={8{13'd656}} ^ (104'd1<<i);
   #1;if(numerical_ok || domain_ok) $fatal(1,"unsupported source bit %0d",i);
  end
  source_words={8{13'd656}};target_exp=31;#1;
  if(numerical_ok) $fatal(1,"wrong target");
  target_exp=32;threshold=12;#1;if(numerical_ok)$fatal(1,"wrong threshold");
  threshold=13;repair_mode=1;#1;if(numerical_ok)$fatal(1,"wrong mode");
  repair_mode=2;proposed_scale=11;#1;if(numerical_ok)$fatal(1,"wrong scale");
  $display("SPEC PASS 213 directed checks");$finish;
 end
endmodule
