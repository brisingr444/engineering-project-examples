module axis_packet_switch (
    input  wire         aclk, aresetn,
    input  wire [127:0] s_axis_tdata,
    input  wire [7:0]   s_axis_tdest,
    input  wire [3:0]   s_axis_tlast, s_axis_tvalid,
    output wire [3:0]   s_axis_tready,
    output wire [127:0] m_axis_tdata,
    output wire [7:0]   m_axis_tdest,
    output wire [3:0]   m_axis_tlast, m_axis_tvalid,
    input  wire [3:0]   m_axis_tready
);
    wire [34:0] head [0:3]; // {last, destination, data}
    wire [3:0] occupied;
    wire [3:0] dequeue [0:3];

    for (genvar i = 0; i < 4; i++) begin : ingress
        reg [34:0] slots [0:1];
        reg rd, wr;
        reg [1:0] count;
        wire pop = dequeue[0][i] | dequeue[1][i] |
                   dequeue[2][i] | dequeue[3][i];
        wire push = s_axis_tvalid[i] && s_axis_tready[i];
        assign occupied[i] = count != 0;
        assign head[i] = slots[rd];
        assign s_axis_tready[i] = count != 2;

        always @(posedge aclk) begin
            if (!aresetn) begin
                rd <= 0;
                wr <= 0;
                count <= 0;
            end else begin
                if (push) begin
                    slots[wr] <= {s_axis_tlast[i], s_axis_tdest[2*i+:2],
                                  s_axis_tdata[32*i+:32]};
                    wr <= ~wr;
                end
                if (pop) rd <= ~rd;
                case ({push,pop})
                    2'b10: count <= count + 1'b1;
                    2'b01: count <= count - 1'b1;
                    default: count <= count;
                endcase
            end
        end
    end

    for (genvar o = 0; o < 4; o++) begin : egress
        reg locked;
        reg [1:0] owner, rr_start;
        wire [3:0] requests;
        for (genvar i = 0; i < 4; i++) begin : decode
            assign requests[i] = occupied[i] && head[i][33:32] == 2'(o);
        end

        reg [1:0] selected;
        always @* begin
            selected = owner;
            if (!locked) begin
                // Reverse scan lets the nearest request overwrite the others.
                for (integer d = 3; d >= 0; d--)
                    if (requests[2'(rr_start + d[1:0])])
                        selected = rr_start + d[1:0];
            end
        end

        wire valid = requests[selected];
        wire transfer = valid && m_axis_tready[o];
        assign m_axis_tvalid[o] = valid;
        assign {m_axis_tlast[o], m_axis_tdest[2*o+:2], m_axis_tdata[32*o+:32]} =
            valid ? head[selected] : 35'b0;
        assign dequeue[o] = transfer ? (4'b0001 << selected) : 4'b0;

        always @(posedge aclk) begin
            if (!aresetn) begin
                locked <= 0;
                owner <= 0;
                rr_start <= 0;
            end else if (valid) begin
                owner <= selected;
                if (transfer && m_axis_tlast[o]) begin
                    locked <= 0;
                    rr_start <= selected + 1'b1;
                end else begin
                    locked <= 1;
                end
            end
        end
    end
endmodule
