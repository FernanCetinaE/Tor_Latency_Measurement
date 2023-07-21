# Basic script to test the path of a relay from https://stem.torproject.org/tutorials/to_russia_with_love.html
# But updated to run on Python 3.9 with BytesIO instead of StringIO
# And example how to custom your own path
from io import BytesIO
import time

import pycurl

import stem.control

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://metrics.torproject.org/rs.html#details/379FB450010D17078B3766C2273303C358C3A442

EXIT_FINGERPRINT = 'A0B5B5906EB13F213D7CA9AFEC91934BE3A5930F'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

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


with stem.control.Controller.from_port() as controller:
  controller.authenticate()

  relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]
  
  try:
     time_taken = scan(controller, ['000A10D43011EA4928A35F610405F92B4433B4DC','000F3EB75342BE371F1D8D3FAE90890AEB5664EE',EXIT_FINGERPRINT])
     print('CUSTOM => %0.2f seconds' % (time_taken))
  except Exception as exc:
     print('CUSTOM FAILED => %s' % (exc))
  for fingerprint in relay_fingerprints:
    try:
      print('Connecting to %s' % (fingerprint))
      time_taken = scan(controller, [fingerprint, EXIT_FINGERPRINT])
      print('%s => %0.2f seconds' % (fingerprint, time_taken))
    except Exception as exc:
      print('%s => %s' % (fingerprint, exc))