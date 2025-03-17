import ssl
from ftplib import FTP_TLS, FTP
import argparse
from pathlib import Path
import logging
LOG_FILENAME = "/output/client_ftp.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.NOTSET,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)
log = logging.getLogger(__name__)

# Define FTP server details
FTP_USER = "ftpuser"
FTP_PASS = "ultra!secret!password"
REMOTE_FILE = "test.txt"
LOCAL_FILE = "/app/test.txt"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FTP Client')
    parser.add_argument('--host', type=str, required=True, help='FTP server hostname')
    parser.add_argument('--port', type=int, default=21, help='FTP server port (default: 21)')
    parser.add_argument('--tls', action='store_true', help='Use TLS for secure connection')
    parser.add_argument('--user-host', type=str, help='username has format user@user-host for proxy')
    args = parser.parse_args()

    # Define FTP server details
    FTP_SERVER = args.host
    FTP_PORT = args.port

    if args.user_host:
        FTP_USER = f"{FTP_USER}@{args.user_host}"

    if args.tls:
        # Create SSL context that does NOT verify the server certificate
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Connect to the FTP server with TLS (without verifying certificate)
        ftps = FTP_TLS(context=ssl_context, timeout=30)
        ftps.set_pasv(1)
        ftps.connect(FTP_SERVER, FTP_PORT)
        log.info(f'Logging in with user {FTP_USER} to {FTP_SERVER}:{FTP_PORT}')
        ftps.login(FTP_USER, FTP_PASS)
        log.info("Logged in to FTP server with TLS")

        # Secure data connection
        ftps.prot_p()
        log.info("Secured data connection")

        # Download the file securely
        with open(LOCAL_FILE, "wb") as f:
            ftps.retrbinary(f"RETR {REMOTE_FILE}", f.write, blocksize=1024)
        log.info("Downloaded file")

        # Close the connection
        ftps.quit()
        log.info("Closed connection")

    else:
        # Connect to the FTP server
        ftp = FTP(timeout=30)
        ftp.set_pasv(1)
        ftp.connect(FTP_SERVER, FTP_PORT)
        log.info(f'Logging in with user {FTP_USER} to {FTP_SERVER}:{FTP_PORT}')
        ftp.login(FTP_USER, FTP_PASS)
        log.info("Logged in to FTP server")

        # Download the file
        with open(LOCAL_FILE, "wb") as f:
            ftp.retrbinary(f"RETR {REMOTE_FILE}", f.write, blocksize=1024)
        log.info("Downloaded file")

        # Close the connection
        ftp.quit()
        log.info("Closed connection")

    Path(LOCAL_FILE).unlink()
    log.info("Deleted local file")