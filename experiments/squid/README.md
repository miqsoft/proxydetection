# Findings:
- httpproxy_ftp: uses http instead of ftp between client and proxy
- httpproxy_ftps: is not supported (maybe not even possible)
- httpproxy_http3: downgrades to http2

# Todos:
- test all three modes? : forward proxy, reverse proxy, SSL-Bump Mode (TLS Interception/Termination)
- test authentication