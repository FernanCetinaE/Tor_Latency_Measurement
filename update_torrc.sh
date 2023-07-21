#!/bin/bash

# Execute tor --hash-password and save the response to a variable
hashed_password=$(tor --hash-password your_hash)

# Replace the value of HashedControlPassword in the "torrc" file
torrc_file="torrc"  # Replace with the actual path to your torrc file
if grep -q '^HashedControlPassword ' "$torrc_file"; then
  sed -i "s|^HashedControlPassword .*|HashedControlPassword $hashed_password|" "$torrc_file"
else
  echo "HashedControlPassword $hashed_password" >> "$torrc_file"
fi

# Start the Tor service with the updated torrc configuration
tor -f "$torrc_file"
