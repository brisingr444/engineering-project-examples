`timescale 1ns/1ps
module tb_axis_packet_switch;
    reg aclk = 0, aresetn = 0;
    always #5 aclk = ~aclk;
    reg [127:0] s_axis_tdata = 0;
    reg [7:0] s_axis_tdest = 0;
    reg [3:0] s_axis_tvalid = 0, s_axis_tlast = 0, m_axis_tready = 15;
    wire [127:0] m_axis_tdata;
    wire [7:0] m_axis_tdest;
    wire [3:0] s_axis_tready, m_axis_tvalid, m_axis_tlast;
    axis_packet_switch dut (.*);

    // Reference streams contain only externally accepted source beats.
    reg [34:0] expected [0:3][0:255];
    int written[4], read_pos[4], in_pkts[4], out_pkts[4], out_beats[4];
    int frame_source[4]; // -1 between frames
    bit [3:0] stalled;
    reg [34:0] held[4];
    bit contention, require_four;
    int service_count, parallel_cycles;
    bit [15:0] routes;
    int flushed_beats, flushed_packets;
    always @(posedge aclk) begin : scoreboard
        integer src;
        reg [34:0] payload;
        if (!aresetn) begin
            for (int i = 0; i < 4; i++) begin
                for (int k = read_pos[i]; k < written[i]; k++) begin
                    flushed_beats++;
                    if (expected[i][k][34]) flushed_packets++;
                end
                written[i] = 0;
                read_pos[i] = 0;
                in_pkts[i] = 0;
                out_pkts[i] = 0;
                out_beats[i] = 0;
                frame_source[i] = -1;
            end
            stalled = 0;
        end else begin
            if ($isunknown(m_axis_tvalid) || $isunknown(s_axis_tready))
                $fatal(1,"unknown handshake");
            if (require_four && (m_axis_tvalid & m_axis_tready) !== 4'hf)
                $fatal(1,"bubble on disjoint saturated routes");
            if ((m_axis_tvalid & m_axis_tready) == 15) parallel_cycles++;
            for (int o = 0; o < 4; o++) begin
                payload = {m_axis_tlast[o], m_axis_tdest[2*o+:2], m_axis_tdata[32*o+:32]};
                if (stalled[o] && (!m_axis_tvalid[o] || payload !== held[o]))
                    $fatal(1,"output %0d changed while stalled",o);
                stalled[o] = m_axis_tvalid[o] && !m_axis_tready[o];
                held[o] = payload;
                if (m_axis_tvalid[o] && m_axis_tready[o]) begin
                    src = int'(unsigned'(payload[31:30]));
                    if ($isunknown(payload) || payload[33:32] != o ||
                        read_pos[src] >= written[src] ||
                        expected[src][read_pos[src]] !== payload)
                        $fatal(1,"unexpected output %0d beat %h",o,payload);
                    if (frame_source[o] >= 0 && frame_source[o] != src)
                        $fatal(1,"frame interleaved on output %0d",o);
                    frame_source[o] = payload[34] ? -1 : src;
                    if (contention && (o != 0 || src != service_count % 4))
                        $fatal(1,"round-robin order at transfer %0d",service_count);
                    if (contention) service_count++;
                    routes[4*src+o] = 1;
                    read_pos[src]++;
                    out_beats[o]++;
                    if (payload[34]) out_pkts[o]++;
                end
            end
            for (int i = 0; i < 4; i++)
                if (s_axis_tvalid[i] && s_axis_tready[i]) begin
                    if (written[i] >= 256) $fatal(1,"scoreboard overflow");
                    expected[i][written[i]] = {s_axis_tlast[i],s_axis_tdest[2*i+:2],
                                               s_axis_tdata[32*i+:32]};
                    written[i]++;
                    if (s_axis_tlast[i]) in_pkts[i]++;
                    if (written[i]-read_pos[i] > 2) $fatal(1,"FIFO capacity");
                end
        end
    end

    // Drivers enter and return on falling edges. One thread drives each lane.
    task automatic beat(input int i, dest, frame_id, seq_id, input bit last);
        s_axis_tdata[i*32+:32] = {i[1:0],frame_id[15:0],seq_id[13:0]};
        s_axis_tdest[i*2+:2] = dest[1:0];
        s_axis_tlast[i] = last;
        s_axis_tvalid[i] = 1;
        do @(posedge aclk); while (!s_axis_tready[i]);
        @(negedge aclk);
        s_axis_tvalid[i] = 0;
    endtask

    task automatic burst(input int i, dest, base, n);
        for (int k = 0; k < n; k++) beat(i,dest,base+k,0,1);
    endtask

    task automatic report_drain(input int epoch);
        int accepted, delivered;
        accepted = 0;
        delivered = 0;
        m_axis_tready = 15;
        repeat (12) @(negedge aclk);
        for (int i = 0; i < 4; i++) begin
            if (read_pos[i] != written[i] || frame_source[i] != -1)
                $fatal(1,"epoch %0d lane %0d failed to drain",epoch,i);
            accepted += in_pkts[i];
            delivered += out_pkts[i];
            $display("epoch %0d port %0d packets in=%0d out=%0d",epoch,i,in_pkts[i],out_pkts[i]);
        end
        if (accepted != delivered || m_axis_tvalid !== 0) $fatal(1,"drain mismatch");
        $display("epoch %0d total packets in=%0d out=%0d",epoch,accepted,delivered);
    endtask

    wire [3:0] contenders = dut.egress[0].requests;
    wire [1:0] grant = dut.egress[0].selected;
    string trace_path;
    wire locked = dut.egress[0].locked;
    initial begin
        repeat (2) @(negedge aclk);
        aresetn = 1;
        contention = 1;
        m_axis_tready[0] = 0;
        fork
            burst(0,0,0,8);
            burst(1,0,0,8);
            burst(2,0,0,8);
            burst(3,0,0,8);
            begin
                if (!$value$plusargs("TRACE=%s",trace_path))
                    trace_path = "contention.vcd";
                $dumpfile(trace_path);
                $dumpvars(0,aclk,contenders,grant,locked,s_axis_tvalid,s_axis_tready,
                          m_axis_tvalid,m_axis_tready,m_axis_tlast,m_axis_tdata);
                repeat (4) @(negedge aclk);
                if (contenders !== 15 || s_axis_tready !== 0) $fatal(1,"contention setup");
                m_axis_tready[0] = 1;
                repeat (8) @(negedge aclk);
                $dumpoff;
            end
        join
        repeat (8) @(negedge aclk);
        if (service_count != 32) $fatal(1,"incomplete contention run");
        contention = 0;

        for (int offset = 0; offset < 4; offset++) begin
            fork
                burst(0,offset,20+8*offset,8);
                burst(1,(1+offset)%4,20+8*offset,8);
                burst(2,(2+offset)%4,20+8*offset,8);
                burst(3,(3+offset)%4,20+8*offset,8);
                begin
                    @(negedge aclk);
                    require_four = 1;
                    repeat (8) @(negedge aclk);
                    require_four = 0;
                end
            join
        end
        if (routes != '1 || parallel_cycles < 32) $fatal(1,"route coverage");

        // Lane 2 owns output 0. Lane 0 challenges it during the first stall.
        // Leave the owner's FIFO empty after beat 0 while lane 0 is waiting.
        m_axis_tready[0] = 0;
        beat(2,0,80,0,0);
        fork
            burst(1,1,100,32);
            begin : stalls
                int before_count;
                beat(0,0,80,0,1);
                for (int k = 0; k < 3; k++) begin
                    if (k != 0) beat(2,0,80,k,k == 2);
                    before_count = out_beats[1];
                    repeat (3) @(negedge aclk);
                    if (out_beats[1] == before_count || m_axis_tvalid[0] !== 1 ||
                        m_axis_tdata[31:30] !== 2'd2) $fatal(1,"isolation or ownership");
                    m_axis_tready[0] = 1;
                    @(negedge aclk);
                    if (k < 2) begin
                        repeat (2) begin
                            if (m_axis_tvalid[0] !== 0) $fatal(1,"grant lost in valid gap");
                            @(negedge aclk);
                        end
                        m_axis_tready[0] = 0;
                    end
                end
            end
        join
        report_drain(1);

        m_axis_tready[3] = 0;
        burst(3,3,200,2);
        if (!m_axis_tvalid[3] || s_axis_tready[3]) $fatal(1,"reset setup");
        aresetn = 0;
        @(negedge aclk);
        if (m_axis_tvalid !== 0 || s_axis_tready !== 15 ||
            flushed_beats != 2 || flushed_packets != 2) $fatal(1,"reset flush");
        $display("reset flushed beats=%0d completed input packets=%0d",flushed_beats,flushed_packets);
        aresetn = 1;
        m_axis_tready = 15;
        for (int i = 0; i < 4; i++) beat(i,3-i,300,0,1);
        report_drain(2);
        $display("PASS axis_packet_switch");
        $finish;
    end
    initial #20000 $fatal(1,"watchdog expired");
endmodule
