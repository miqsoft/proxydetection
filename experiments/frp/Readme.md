# Does not work
- tcp_ftp, tcp_ftps: fails even if data port is also shared;
- udp_https3: does not work (multiple github issues exist with telling not implemented so far)


# Todo:
- (maybe) realize ssh-tunnel-gateway (use ssh as client instead of frpc)
- (maybe) test plugins such as http_proxy, socks5, http2https, https2http, https2https

# Version
- frp: 0.61.2