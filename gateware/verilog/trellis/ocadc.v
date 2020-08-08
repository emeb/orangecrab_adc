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
    
    // diagnostics
    output A0, A1, A2, A3, A4,
	
	// USB
	inout USB_DP, USB_DM,
	output USB_PULLUP,
	
	// RGB LED
	output LED1, LED2, LED3,

    // Reset to bootloader without unplugging
	output RST_N,
	input BTN_N
);
	// main reset generator waits > 10us
	reg [7:0] reset_cnt;
	reg reset;
	initial
        reset_cnt <= 6'h00;
    
	always @(posedge CLK)
	begin
		if(reset_cnt != 6'h3f)
        begin
            reset_cnt <= reset_cnt + 6'h01;
            reset <= 1'b1;
        end
        else
            reset <= 1'b0;
	end
    
	// adc reset generator waits > 10us
	reg [7:0] adc_reset_cnt;
	reg reset_adc;
	initial
        adc_reset_cnt <= 6'h00;
    
	always @(posedge clk_adc)
	begin
		if(reset_cnt != 6'h3f)
        begin
            adc_reset_cnt <= adc_reset_cnt + 6'h01;
            reset_adc <= 1'b1;
        end
        else
            reset_adc <= 1'b0;
	end
    
    // control regs
	reg [25:0] ddc_frq;
    reg ddc_ns_ena;
    reg [2:0] ddc_cic_shf;
    reg [1:0] dr; 
    reg [2:0] demod_type;
	always @(posedge clk_adc)
		if(reset_adc)
		begin
            ddc_frq <= 26'd2415919;		// 1.44MHz
			ddc_ns_ena <= 1'b0;         // no noise shaping
			ddc_cic_shf <= 3'b110;      // max gain
            dr <= 2'b00;                // 19.53kSPS
            //dr <= 2'b11;                // 156.25kSPS
            demod_type <= 3'd0;         // AM
		end
    
	//------------------------------
	// ADC input register
	//------------------------------
    (* syn_useioff *) reg signed [isz-1:0] adc_reg;
    always @(posedge clk_adc)
        adc_reg <= adc_data;
    
	//------------------------------
	// DDC
	//------------------------------
    wire signed [dsz-1:0] ddc_i, ddc_q;
    wire ddc_v;
    wire diag;
    ddc_14 #(
        .isz(isz),
        .fsz(fsz),
        .osz(dsz)
    )
    u_ddc(
        .clk(clk_adc), .reset(reset_adc),
        .in(adc_reg),
		.dr(dr),
        .frq(ddc_frq),
        .ns_ena(ddc_ns_ena),
        .cic_shf(ddc_cic_shf),
        .sathld(),
        .valid(ddc_v),
        .i_out(ddc_i), .q_out(ddc_q),
        .diag(diag)
    );
    
	//------------------------------
	// Demods
	//------------------------------
    wire signed [dsz-1:0] demod_l, demod_r;
    wire demod_v;
//`define BYPASS_DEMODS
`ifdef BYPASS_DEMODS
    demods #(
        .dsz(dsz)
    )
    u_demods(
        .clk(clk_adc), .reset(reset_adc),
        .i(ddc_i), .q(ddc_q),
        .ena(ddc_v),
		.type(demod_type),
        .valid(demod_v),
        .l_out(demod_l), .r_out(demod_r)
    );

	//------------------------------
	// test oscillator
	//------------------------------
	wire signed [15:0] sine, cosine;
	sine_osc usine(
		.clk(clk_adc),
		.reset(reset_adc),
		.freq(219902326),   // 1kHz @ Fs = 19.5kHz 
		.load(demod_v),
		.sin(demod_l),
		.cos(demod_r)
	);
`else    
    demods #(
        .dsz(dsz)
    )
    u_demods(
        .clk(clk_adc), .reset(reset_adc),
        .i(ddc_i), .q(ddc_q),
        .ena(ddc_v),
		.type(demod_type),
        .valid(demod_v),
        .l_out(demod_l), .r_out(demod_r)
    );
`endif

    //------------------------------
	// PDM DAC
	//------------------------------
	pdm_dac udac(
		.clk(clk_adc), .reset(reset_adc),
		.load(demod_v),
		.lin(demod_l), .rin(demod_r),
		.lpdm(PDM_L), .rpdm(PDM_R)
	);
    
    // Diagnostics
    assign A0 = demod_v;
    assign A1 = ddc_v;
    assign A2 = diag;
    
	//------------------------------
	// Activity indicators
	//------------------------------
    // main clock
    reg [23:0] main_div;
    always @(posedge CLK)
        if(reset)
            main_div <= 0;
        else
            main_div <= main_div + 1;
        
    // adc clock
    reg [23:0] adc_div;
    always @(posedge clk_adc)
        if(reset_adc)
            adc_div <= 0;
        else
            adc_div <= adc_div + 1;
    
	assign {LED1,LED2,LED3} = {main_div[23],adc_div[23],PDM_L};
    
	/* Reset logic on button press */
	reg reset_sr = 1'b1;
	always @(posedge CLK) begin
		reset_sr <= {BTN_N};
	end
	assign RST_N = reset_sr;
    
endmodule
