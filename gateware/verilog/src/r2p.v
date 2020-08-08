// r2p.v - CORDIC Rectangular to Polar conversion
// 08-06-20 E. Brombaugh

`default_nettype none

module r2p #(
    parameter dsz = 16, // input size
    parameter psz = 16  // phase output size
)
(
    input clk, reset,
    input signed [dsz-1:0] x, y,
    input ena,
    output reg valid,
    output reg [dsz-1:0] mag,
    output reg signed [psz-1:0] angle
);
    // extra internal params
    parameter iterations = 16;
    parameter gsz = 4;      // guard bits
    parameter k = 39796;    // gain scale factor
    
    // initial values - handle x<0
    reg signed [dsz-1:0] xi, yi;
    reg signed [psz-1:0] ai;
    reg ena_d1;
    always @(posedge clk)
    begin
        if(reset)
        begin
        end
        else
        begin
            if(ena)
            begin
                xi <= x[dsz-1] ? -x : x;
                yi <= x[dsz-1] ? -y : y;
                ai <= x[dsz-1] ? {1'b1,{dsz-1{1'b0}}} : 0;
            end
            ena_d1 <= ena;
        end
    end
    
    // Iteration State Machine
    reg State, run_d1;
    reg [3:0] itr, itr_d1;
    wire run = State;
    always @(posedge clk)
    begin
        if(reset)
        begin
            State <= 0;
            itr <= 0;
            itr_d1 <= 0;
            run_d1 <= 0;
        end
        else
        begin
            case(State)
                1'b0:   // Wait
                begin
                    if(ena_d1)
                    begin
                        State <= 1'b1;
                        itr <= 4'd0;
                    end
                end
                
                1'b1:   // Run
                begin
                    if(&itr)
                        State <= 1'b0;
                    else
                        itr <= itr + 4'd1;
                end
            endcase
            itr_d1 <= itr;
            run_d1 <= run;
        end
    end
    
    // look up angle per iteration
    reg signed [psz-1:0] phi;
    reg signed [psz-1:0] LUT[0:iterations-1];
    initial
       $readmemh("../src/r2p_phi_lut.memh", LUT);
    
    always @(posedge clk)
    begin
        if(reset)
            phi <= 0;
        else
            phi <= LUT[itr];
    end
    
    // Iteration Accumulators
    reg signed [dsz+gsz+1:0] xacc;
    reg signed [dsz+gsz:0] yacc;
    reg signed [psz-1:0] aacc;
    wire signed [dsz+gsz+1:0] sx = xacc>>>itr_d1;
    wire signed [dsz+gsz:0] sy = yacc>>>itr_d1;
    always @(posedge clk)
    begin
        if(reset)
        begin
            xacc <= 0;
            yacc <= 0;
            aacc <= 0;
        end
        else
        begin
            if(run & ~run_d1)
            begin
                xacc <= xi<<gsz;
                yacc <= yi<<gsz;
                aacc <= ai;
            end
            else if(run_d1)
            begin
                if(yacc[dsz+gsz])
                begin
                    xacc <= xacc - sy;
                    yacc <= yacc + sx;
                    aacc <= aacc - phi;
                end
                else
                begin
                    xacc <= xacc + sy;
                    yacc <= yacc - sx;
                    aacc <= aacc + phi;
                end                
            end
        end
    end
    
    // scale and hold output
    reg [1:0] done;
    reg [2*dsz:0] mscale;
    wire [dsz:0] uxacc = xacc>>>gsz;
    always @(posedge clk)
    begin
        if(reset)
        begin
            done <= 0;
            mscale <= 0;
            mag <= 0;
            angle <= 0;
            valid <= 0;
        end
        else
        begin
            done <= {done[0],(~run&run_d1)};
            valid <= done[1];
            if(done[0])
                mscale <= uxacc*k;
            if(done[1])
            begin
                angle <= aacc;
                mag <= mscale>>dsz;
            end
        end
    end
endmodule
