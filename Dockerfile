FROM python:3.9

# Update the package lists
RUN apt-get update

# Install Tor
RUN apt-get install -y tor

# Set environment variables
ENV PYCURL_SSL_LIBRARY=openssl \
    PYCURL_SSL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu \
    PYCURL_SSL_LIBRARIES=openssl \
    LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

# Install required packages
RUN apt-get install -y libssl-dev

# Install pycurl and stem using pip
RUN apt-get install -y python3-pip nano curl
RUN pip install pycurl==7.45.2 stem==1.8.0

COPY measure.py /measure.py
COPY automated_paths.py /automated_paths.py
COPY input_file.csv /input_file.csv
COPY torrc /torrc
COPY update_torrc.sh /update_torrc.sh
RUN chmod +x /update_torrc.sh

# Expose the Tor SOCKS proxy port (if needed)
EXPOSE 9051 9050 9030 