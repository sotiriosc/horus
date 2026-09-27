`timescale 1ns/1ps
// SPDX-License-Identifier: CERN-OHL-S-2.0
module tb_campaign;
 parameter TRACE_BITS=96;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0,valid_in=0,sink_ready=0,checker_pause=0;
 reg [103:0] source_words={8{13'd656}};
 reg [15:0] transaction_id=0,source_record_id=0;
 reg [7:0] epoch=0;
 reg [2:0] fault_mode=0,trace_address=0;
 reg [3:0] fault_pattern=0;
 wire ready_in,sink_valid,halted,decision_valid,proposal_seen,detected,replayed,wrong_accept;
 wire [103:0] sink_words,wrong_words;
 wire [15:0] sink_id;wire [7:0] sink_epoch;
 wire [1:0] occupancy,quarantine_occupancy;
 wire [95:0] decision_trace,trace_data;
 bounded_commit_top #(.TRACE_BITS(TRACE_BITS)) top(.*);
 integer seed,mode,cycle=0,sent=0,decided=0,accepted=0,rejected=0;
 integer false_accept=0,false_reject=0,duplicate=0,id_mismatch=0,epoch_mismatch=0;
 integer record_mismatch=0,checker_reject=0,timeouts=0,retry_total=0;
 integer min_cycles=999,max_cycles=0,sum_cycles=0,max_q=0,max_reserved=0;
 integer blocked=0,wrong_false=0,proposals=0,det_count=0,replay_count=0;
 integer start_cycle[0:199],seen[0:199],i,idx,expected_mode,latency;
 reg [31:0] rng;
 reg [95:0] last_trace[0:7];
 integer trace_count=0;
 initial begin
  if(!$value$plusargs("SEED=%d",seed)) seed=1;
  if(!$value$plusargs("MODE=%d",mode)) mode=0;
  rng=seed;epoch=seed;
  for(i=0;i<200;i=i+1) begin start_cycle[i]=0;seen[i]=0;end
  for(i=0;i<8;i=i+1)last_trace[i]=0;
  repeat(4) @(negedge clk);rst_n=1;
 end
 always @(negedge clk) if(rst_n && decided<200) begin
  rng=rng*32'd1664525+32'd1013904223;
  // Identical schedules across modes for each seed, bounded stalls.
  sink_ready=(cycle>=35) && ((cycle%4==0) || rng[25]);
  checker_pause=!(cycle%3==0 || rng[19]);
  valid_in=sent<200 && (cycle%3==0 || rng[30]);
  transaction_id=sent+1;source_record_id=sent+4097;
  fault_mode=(sent%2==1) ? mode : 0;
 end
 always @(posedge clk) if(rst_n) begin
  cycle=cycle+1;
  if(cycle>20000) $fatal(1,"campaign deadline exceeded");
  if(occupancy>2 || quarantine_occupancy>2) $fatal(1,"state bound");
  if(occupancy>max_reserved)max_reserved=occupancy;
  if(quarantine_occupancy>max_q)max_q=quarantine_occupancy;
  if(occupancy==2 && ready_in) $fatal(1,"no full-buffer backpressure");
  if(valid_in && !ready_in)blocked=blocked+1;
  if(valid_in && ready_in) begin start_cycle[sent]=cycle;sent=sent+1;end
  if(proposal_seen)proposals=proposals+1;
  if(detected)det_count=det_count+1;
  if(replayed)replay_count=replay_count+1;
  if(wrong_accept) begin
   if(wrong_words=={8{13'd2064}}) $fatal(1,"negative control was not corrupt");
   wrong_false=wrong_false+1;
  end
  if(sink_valid && sink_ready) begin
   if(sink_id<1 || sink_id>200) $fatal(1,"invalid sink id");
   idx=sink_id-1;
   if(seen[idx])duplicate=duplicate+1;
   seen[idx]=seen[idx]+1;accepted=accepted+1;
   if(sink_words!={8{13'd2064}} || sink_epoch!=seed ||
      (idx%2==1 && mode>=2)) false_accept=false_accept+1;
  end
  #1;
  if(decision_valid) begin
   idx=decision_trace[62:47]-1;
   if(idx!=decided) $fatal(1,"lost/reassigned decision identity");
   if(decision_trace[46:39]!=seed || decision_trace[38:23]!=idx+4097)
     $fatal(1,"protected identity mutated");
   expected_mode=(idx%2==1)?mode:0;
   latency=cycle-start_cycle[idx];
   if(latency>64) $fatal(1,"unbounded decision latency");
   if(latency<min_cycles)min_cycles=latency;
   if(latency>max_cycles)max_cycles=latency;
   sum_cycles=sum_cycles+latency;
   if(!decision_trace[18]) $fatal(1,"decision without proposal in normal campaign");
   if(decision_trace[22]!=(expected_mode!=0)) $fatal(1,"detector status mismatch");
   if(expected_mode!=0 && decision_trace[21:19]!=3) $fatal(1,"localization mismatch");
   if(decision_trace[12:11]!=(expected_mode!=0)) $fatal(1,"retry bound/count");
   if(decision_trace[10] && (!decision_trace[13] || !(&decision_trace[17:14])))
     $fatal(1,"unverified external acceptance");
   if(decision_trace[9]) begin
    rejected=rejected+1;
    if(expected_mode<2)false_reject=false_reject+1;
   end
   if(!decision_trace[17])id_mismatch=id_mismatch+1;
   if(!decision_trace[16])epoch_mismatch=epoch_mismatch+1;
   if(!decision_trace[15])record_mismatch=record_mismatch+1;
   if(decision_trace[9] && !decision_trace[8])checker_reject=checker_reject+1;
   if(decision_trace[8])timeouts=timeouts+1;
   retry_total=retry_total+decision_trace[12:11];
   last_trace[trace_count%8]=decision_trace;trace_count=trace_count+1;
   $display("TRACE %024h",decision_trace);
   decided=decided+1;
   if(decided==200) begin
    valid_in=0;sink_ready=1;checker_pause=0;
    if(sent!=200 || false_accept || false_reject || duplicate || timeouts)
      $fatal(1,"protocol metric violation");
    if(accepted!=(mode<2?200:100) || rejected!=(mode<2?0:100))
      $fatal(1,"missing control outcomes");
    if(proposals!=200 || retry_total!=(mode==0?0:100) ||
       replay_count!=retry_total || det_count!=retry_total) $fatal(1,"transaction count");
    if(id_mismatch!=(mode==3?100:0) || epoch_mismatch!=(mode==4?100:0) ||
       record_mismatch!=(mode==6?100:0) || wrong_false!=(mode==5?100:0))
       $fatal(1,"control did not exercise specified fault");
    if(max_q!=2 || max_reserved!=2 || blocked==0) $fatal(1,"backpressure not exercised");
    for(i=0;i<8;i=i+1) begin
     trace_address=i;#1;
     if(trace_data!==last_trace[i]) $fatal(1,"bounded trace ring mismatch");
    end
    $display("METRICS seed=%0d mode=%0d sent=%0d accepted=%0d rejected=%0d false_accept=%0d false_reject=%0d duplicate=%0d id_mismatch=%0d epoch_mismatch=%0d record_mismatch=%0d checker_reject=%0d timeout=%0d retries=%0d min_cycles=%0d max_cycles=%0d sum_cycles=%0d max_quarantine=%0d max_reserved=%0d backpressure_cycles=%0d negative_false_accept=%0d",seed,mode,sent,accepted,rejected,false_accept,false_reject,duplicate,id_mismatch,epoch_mismatch,record_mismatch,checker_reject,timeouts,retry_total,min_cycles,max_cycles,sum_cycles,max_q,max_reserved,blocked,wrong_false);
    $display("CAMPAIGN PASS");$finish;
   end
  end
 end
endmodule
