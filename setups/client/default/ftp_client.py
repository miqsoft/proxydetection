import ssl
from ftplib import FTP_TLS, FTP
import argparse
from pathlib import Path
import logging
LOG_FILENAME = "/output/client_ftp.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
    args = parser.parse_args()

    # Define FTP server details
    FTP_SERVER = args.host
    FTP_PORT = args.port

    if args.tls:
        # Create SSL context that does NOT verify the server certificate
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Connect to the FTP server with TLS (without verifying certificate)
        ftps = FTP_TLS(context=ssl_context)
        ftps.connect(FTP_SERVER, FTP_PORT)
        ftps.login(FTP_USER, FTP_PASS)
        logging.info("Logged in to FTP server with TLS")

        # Secure data connection
        ftps.prot_p()
        logging.info("Secured data connection")

        # Download the file securely
        with open(LOCAL_FILE, "wb") as f:
            ftps.retrbinary(f"RETR {REMOTE_FILE}", f.write)
        logging.info("Downloaded file")

        # Close the connection
        ftps.quit()
        logging.info("Closed connection")

    else:
        # Connect to the FTP server
        ftp = FTP()
        ftp.connect(FTP_SERVER, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Logged in to FTP server")

        # Download the file
        with open(LOCAL_FILE, "wb") as f:
            ftp.retrbinary(f"RETR {REMOTE_FILE}", f.write)
        logging.info("Downloaded file")

        # Close the connection
        ftp.quit()
        logging.info("Closed connection")

    Path(LOCAL_FILE).unlink()
    logging.info("Deleted local file")