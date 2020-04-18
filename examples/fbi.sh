tshark -i lo -Y 'tcp.flags.push == 1 and tcp.flags.ack == 1' -T text -x
