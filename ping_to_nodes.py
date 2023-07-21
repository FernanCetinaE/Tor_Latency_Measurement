import pandas as pd
from pythonping import ping

def ping_ip(ip):
    try:
        response_time = ping(ip, count=1).rtt_avg_ms
        return response_time
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return None

def main(input_file, output_file):
    try:
        df = pd.read_csv(input_file, names=['fingerprint', 'ip'])
        df['time'] = df['ip'].apply(ping_ip)
        df.to_csv(output_file, index=False, header=False)
        print(f"Results written to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_csv = "nodes_list.csv"
    output_csv = "ping_time_to_nodes.csv"
    main(input_csv, output_csv)
