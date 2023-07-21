from io import BytesIO
import time
import pycurl
import csv
import stem.control

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://metrics.torproject.org/rs.html#details/379FB450010D17078B3766C2273303C358C3A442

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

def query(url):
  output = BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEDATA, output)

  try:
    query.perform()
    #query.close()
    return output.getvalue().decode('utf-8')
  except pycurl.error as exc:
    print("FAIL")
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """

  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()

    check_page = query('https://check.torproject.org/')
    
    if 'Congratulations. This browser is configured to use Tor.' not in check_page:
      raise ValueError("Request didn't have the right content")

    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

def read_csv_file(csv_file):
  with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      if len(row) >= 2:
        yield row[:3]  # Pass the first 3 strings from each row
      elif len(row) == 1:
        yield [row[0], '']  # If there is only 1 string, yield it with an empty string
      else:
        print(f"Skipping line: {row}. Each row should have at least 2 strings.")

def write_to_csv(strings_array, number, csv_file):
  # Check if the number is a valid numeric value
  if not isinstance(number, (int, float)):
    number_value = -1  # Insert -1 if the number is missing or not a valid numeric value
  else:
    number_value = number

  # Combine the strings and the number into a list for CSV writing
  data = strings_array + [number_value]

  # Write to CSV file in append mode to add a new line on each call
  with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(data)

if __name__ == "__main__":
    SOCKS_PORT = 9050
    CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

    csv_file = "/input_file.csv"  # Replace with the actual name of your CSV file

    with stem.control.Controller.from_port() as controller:
        controller.authenticate()

        for path in read_csv_file(csv_file):
            try:
              if len(path) >= 2:
                time_taken = scan(controller, path)
                print(f"{path} => {time_taken:.2f} seconds")
                write_to_csv(path, time_taken, "latency_output.csv")
              else:
                print(f"Skipping path: {path}. It should have at least 2 strings.")
            except Exception as exc:
              print(f"{path} => {exc}")
              write_to_csv(path, -1, "latency_output.csv")