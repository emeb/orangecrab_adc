// tb_ocadc.v - testbench for rxadc on orangecrab
// 07-28-20 E. Brombaugh

`timescale 1ns/1ps
`default_nettype none

module tb_ocadc;
    reg clk_adc;
	reg start;
	reg err;
	real phs, frq;
	reg signed [9:0] adc_data;
	wire PDM_L, PDM_R;
	wire LED1, LED2, LED3;
	reg BTN_N;
    wire RST_N;
    
    // 40MHz clock source
    always
        #12.5 clk_adc = ~clk_adc;
    
    // reset
    initial
    begin
`ifdef icarus
  		$dumpfile("tb_ocadc.vcd");
		$dumpvars;
`endif
        
        // init regs
        clk_adc = 1'b0;
		phs = 0;
		frq = 6.2832*1.441e6/50e6;
		adc_data = 10'd0;
        BTN_N = 1'b1;
        
`ifdef icarus
        // stop after 4ms
		#5000000 $finish;
`endif
    end
    
    // pop the PDM accums to get them working
    initial
    begin
        #1800000 force uut.udac.lsdacc = 0;
        force uut.udac.rsdacc = 0;
        #100 release uut.udac.lsdacc;
        release uut.udac.rsdacc;
    end
    
	// ADC data
	always @(negedge clk_adc)
	begin
		adc_data <= 100*$sin(phs);
		phs <= phs + frq;
	end
	
    // Unit under test
	ocadc uut(
		// rxadc board interface on PMODs P403, P404
		.clk_adc(clk_adc),
		.adc_data(adc_data),
		
		// PDM outputs on P401
		.PDM_L(PDM_L), .PDM_R(PDM_R),
		
		// LED - via drivers
		.LED1(LED1), .LED2(LED2), .LED3(LED3),
        
        // reboot
        .BTN_N(BTN_N),
    	.RST_N(RST_N)
	);
endmodule
