# Info:
- vmess_tcp: taken from example: https://github.com/XTLS/Xray-examples/tree/main/VMess-TCP
- vless_tcp: taken from example: https://github.com/XTLS/Xray-examples/tree/main/VLESS-TCP
- vless_tcp_tls: taken from example: https://github.com/XTLS/Xray-examples/tree/main/VLESS-TCP-TLS
- trojan_tcp_tls: taken from example: https://github.com/XTLS/Xray-examples/tree/main/Trojan-TCP-TLS%20(minimal)
- socks5_tls: taken from example: https://github.com/XTLS/Xray-examples/tree/main/Socks5-TLS -> did not work
- shadowsocks: taken from example: https://github.com/XTLS/Xray-examples/tree/main/Shadowsocks-TCP 
- trojan_tcp_tls: does not work since outdated: https://github.com/XTLS/Xray-examples/tree/main/Trojan-TCP-XTLS -> tried like this: https://github.com/XTLS/Xray-examples/tree/main/VLESS-TCP-XTLS-Vision did also not work
- vless_tcp_xtls_vision: taken from example: https://github.com/XTLS/Xray-examples/tree/main/VLESS-TCP-XTLS-Vision

# Does not work
- http3: http3 is not supported over socks5 proxy

# Todo:
- maybe test websocket, mKCP for transport
- try xhttp3?!: https://github.com/XTLS/Xray-examples/tree/main/VLESS-XHTTP3-Nginx

# Version
- XRay: 25.3.6