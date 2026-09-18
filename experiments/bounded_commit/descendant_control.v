// SPDX-License-Identifier: CERN-OHL-S-2.0
// NEGATIVE CONTROL ONLY. Equality to a descendant is not independent truth.
module descendant_control(input wire available,
 input wire [103:0] candidate,descendant_reference,output wire accept);
 assign accept=available && candidate==descendant_reference;
endmodule
