// ocadc.v - top level for ocadc - orangecrab ADC
// 07-28-20 E. Brombaugh

`default_nettype none

module ocadc #(
    parameter isz = 10,
              fsz = 26,
              dsz = 16
)(
	// 48MHz On-board Oscillator
	input  CLK,
    
    // ADC clock
    input clk_adc,
    
    // ADC input data
    input signed [isz-1:0] adc_data,
    
    // PDM audio output
    output PDM_L, PDM_R,
	
	// USB
	inout USB_DP, USB_DM,
	output USB_PULLUP,
	
	// RGB LED
	output LED1, LED2, LED3,

    // Reset to bootloader without unplugging
	output RST_N,
	input BTN_N
);
	// reset generator waits > 10us
	reg [7:0] reset_cnt;
	reg reset;
	initial
        reset_cnt <= 6'h00;
    
	always @(posedge clk_adc)
	begin
		if(reset_cnt != 6'h3f)
        begin
            reset_cnt <= reset_cnt + 6'h01;
            reset <= 1'b1;
        end
        else
            reset <= 1'b0;
	end
    
    // control regs
	reg [25:0] ddc_frq;
    reg ddc_ns_ena;
    reg [2:0] ddc_cic_shf;
    reg [1:0] dr; 
	always @(posedge clk_adc)
		if(reset)
		begin
            ddc_frq <= 26'd1932735;		// 1.44MHz
			ddc_ns_ena <= 1'b0;         // no noise shaping
			ddc_cic_shf <= 3'b011;      // max gain
            dr <= 2'b00;                // 19.53kSPS
            //dr <= 2'b11;                // 156.25kSPS
		end
    
	//------------------------------
	// DDC
	//------------------------------
    wire signed [dsz-1:0] ddc_i, ddc_q;
    wire ddc_v;
    ddc_14 #(
        .isz(isz),
        .fsz(fsz),
        .osz(dsz)
    )
    u_ddc(
        .clk(clk_adc), .reset(reset),
        .in(adc_data),
		.dr(dr),
        .frq(ddc_frq),
        .ns_ena(ddc_ns_ena),
        .cic_shf(ddc_cic_shf),
        .sathld(),
        .valid(ddc_v),
        .i_out(ddc_i), .q_out(ddc_q)
    );
    
	//------------------------------
	// PDM DAC
	//------------------------------
	pdm_dac udac(
		.clk(clk_adc),
		.reset(reset),
		.load(ddc_v),
		.lin(ddc_i), .rin(ddc_q),
		.lpdm(PDM_L), .rpdm(PDM_R)
	);
	
	// drive LEDs from GPIO
	assign {LED1,LED2,LED3} = 3'b000;
    
	/* Reset logic on button press */
	reg reset_sr = 1'b1;
	always @(posedge CLK) begin
		reset_sr <= {BTN_N};
	end
	assign RST_N = reset_sr;
    

endmodule
