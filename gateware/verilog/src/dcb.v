// dcb.v - DC block
// 08-06-20 E. Brombaugh

`default_nettype none

module dcb #(
    parameter dsz = 16,         // input size
    parameter dc_coeff = 10     // corner freq
)
(
    input clk, reset,
    input signed [dsz-1:0] in,
    input ena,
    output valid,
    output reg signed [dsz-1:0] out
);
    // accumulate DC and subtract
    reg signed [dsz+dc_coeff:0] dcb_acc;
    reg signed [dsz:0] dcb_out;
    reg [1:0] valid_pipe;
    always @(posedge clk)
    begin
        if(reset)
        begin
            dcb_acc <= 0;
            dcb_out <= 0;
            valid_pipe <= 0;
        end
        else
        begin
            if(ena)
            begin
                dcb_acc <= dcb_acc + dcb_out;
                dcb_out <= in - (dcb_acc>>>dc_coeff);
            end
            
            valid_pipe <= {valid_pipe[0],ena};
        end
    end
        
    // saturate DC block output
    wire signed [dsz-1:0] sat_out;
    sat #(
        .isz(dsz+1),
        .osz(dsz)
    )
    u_sat(
        .in(dcb_out),
        .out(sat_out)
    );
    
    always @(posedge clk)
    begin
        if(reset)
            out <= 0;
        else
            out <= sat_out;
    end
    assign valid = valid_pipe[1];
endmodule
