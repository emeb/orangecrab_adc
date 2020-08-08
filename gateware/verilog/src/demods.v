// demods.v - baseband demodulation
// 08-06-20 E. Brombaugh

`default_nettype none

module demods #(
    parameter dsz = 16 // input size
)
(
    input clk, reset,
    input signed [dsz-1:0] i, q,
    input ena,
	input [2:0] type,
    output reg valid,
    output reg signed [dsz-1:0] l_out, r_out
);
    // Rect->Polar conversion
    wire signed [dsz-1:0] mag, angle;
    wire r2p_v;
    r2p #(
        .dsz(dsz),
        .psz(dsz)
    )
    u_r2p(
        .clk(clk),
        .reset(reset),
        .x(i), .y(q),
        .ena(ena),
        .mag(mag), .angle(angle),
        .valid(r2p_v)
    );
    
    //-------------------------
    // AM demod
    //-------------------------
    // DC block on magnitude
    wire signed [dsz-1:0] am;
    wire am_v;
    dcb #(
        .dsz(dsz),
        .dc_coeff(10)
    )
    u_am_dcb(
        .clk(clk),
        .reset(reset),
        .in(mag),
        .ena(r2p_v),
        .out(am),
        .valid(am_v)
    );
    
    //-------------------------
    // NBFM demod
    //-------------------------
    // differentiate angle to get frequency
    reg signed [dsz-1:0] angle_d1, rfrq;
    reg r2p_v_d1;
    always @(posedge clk)
        if(reset)
        begin
            angle_d1 <= 0;
            rfrq <= 0;
            r2p_v_d1 <= 0;
        end
        else
        begin
            if(r2p_v)
            begin
                angle_d1 <= angle;
                rfrq <= angle - angle_d1;
            end
            r2p_v_d1 <= r2p_v;
        end
    
    // DC block on frequency to remove residual freq error
    wire signed [dsz-1:0] rfm;
    wire rfm_v;
    dcb #(
        .dsz(dsz),
        .dc_coeff(10)
    )
    u_fm_dcb(
        .clk(clk),
        .reset(reset),
        .in(rfrq),
        .ena(r2p_v_d1),
        .out(rfm),
        .valid(rfm_v)
    );
    
    // De-emphasis
    reg signed [dsz+2:0] nbfm_de_acc;
    reg nbfm_v;
    always @(posedge clk)
    begin
        if(reset)
        begin
            nbfm_de_acc <= 0;
            nbfm_v <= 0;
        end
        else
        begin
            if(rfm_v)
                nbfm_de_acc <= nbfm_de_acc - (nbfm_de_acc>>7) + rfm;
            
            nbfm_v <= rfm_v;            
        end
    end
    wire signed [dsz-1:0] nbfm = nbfm_de_acc>>3;
    
    //-------------------------
    // Output Mux
    //-------------------------
    always @(posedge clk)
    begin
        if(reset)
        begin
            l_out <= 0;
            r_out <= 0;
            valid <= 0;
        end
        else
        begin
            case(type)
                3'd0:   // AM
                begin
                    l_out <= am;
                    r_out <= am;
                    valid <= am_v;
                end
                
                3'd2:   // NBFM
                begin
                    l_out <= nbfm;
                    r_out <= nbfm;
                    valid <= nbfm_v;
                end
                
                3'd6:   // RAW
                begin
                    l_out <= i;
                    r_out <= q;
                    valid <= ena;
                end
                
                default:
                begin
                    l_out <= i;
                    r_out <= q;
                    valid <= ena;
                end
            endcase
        end
    end
endmodule
