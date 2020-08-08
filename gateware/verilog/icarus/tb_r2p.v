// tb_r2p.v - testbench for CORDIC r2p
// 08-06-20 E. Brombaugh

`timescale 1ns/1ps
`default_nettype none

module tb_r2p;
    reg clk, reset;
	real phs, frq;
    reg ena;
    reg [7:0] enacnt;
	reg signed [15:0] x, y;
    wire valid;
    wire [15:0] mag;
    wire signed [15:0] angle;
    
    // reset
    initial
    begin
`ifdef icarus
  		$dumpfile("tb_r2p.vcd");
		$dumpvars;
`endif
        
        // init regs
        clk = 1'b0;
        reset = 1'b1;
		phs = 0;
		frq = 6.2832*500e3/50e6;
		x = 16'd0;
		y = 16'd0;
        ena = 0;
        enacnt = 0;
        
        #100 reset = 0;
        
`ifdef icarus
        // stop after 4ms
		#1000000 $finish;
`endif
    end
        
    // 40MHz clock source
    always
        #12.5 clk = ~clk;
    
    // 1/256 enable rate
    always @(posedge clk)
    begin
        enacnt <= enacnt + 1;
        ena <= &enacnt;
    end
    
	// input data
	always @(negedge clk)
        if(ena)
        begin
            x <= 20000*$cos(phs);
            y <= 20000*$sin(phs);
            phs <= phs + frq;
        end
	
    // Unit under test
	r2p uut(
		.clk(clk),
		.reset(reset),
		.ena(ena),
        .x(x), .y(y),
        .valid(valid),
        .mag(mag), .angle(angle)
	);
endmodule
