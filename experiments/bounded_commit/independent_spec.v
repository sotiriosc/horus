// SPDX-License-Identifier: CERN-OHL-S-2.0
// Independent, deliberately narrow integer specification. No DUT helpers.
// Source domain: eight positive words, exponent 10, fraction 16; target 32.
module independent_spec (
 input wire [103:0] source_words,
 input wire [5:0] target_exp, threshold,
 input wire [1:0] repair_mode,
 input wire [103:0] proposed_words,
 input wire [5:0] proposed_scale,
 output reg domain_ok,
 output reg [103:0] expected_words,
 output wire numerical_ok
);
 integer lane, original_exponent, normalized_exponent;
 reg [12:0] original_word;
 always @* begin
  domain_ok = (target_exp == 32 && threshold == 13 && repair_mode == 2);
  expected_words = 104'd0;
  original_word = 0; original_exponent = 0; normalized_exponent = 0;
  for (lane=0; lane<8; lane=lane+1) begin
   original_word = source_words[lane*13 +: 13];
   original_exponent = (original_word >> 6) & 63;
   if (original_word != 13'd656) domain_ok = 0;
   // In this domain all exponents equal 10: common offset = target - 10.
   normalized_exponent = original_exponent + target_exp - 10;
   expected_words[lane*13 +: 13] =
     (original_word & 13'h103f) | (normalized_exponent << 6);
  end
 end
 assign numerical_ok = domain_ok && proposed_scale == 10 &&
                       proposed_words == expected_words;
endmodule
