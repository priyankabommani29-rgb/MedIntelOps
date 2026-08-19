from prometheus_client import start_http_server
from prometheus_client import Gauge
import psutil
import time

cpu_usage = Gauge(
    'cpu_usage_percent',
    'CPU Usage'
)

memory_usage = Gauge(
    'memory_usage_percent',
    'Memory Usage'
)

def monitor():

    while True:

        cpu_usage.set(
            psutil.cpu_percent()
        )

        memory_usage.set(
            psutil.virtual_memory().percent
        )

        time.sleep(5)

if __name__ == "__main__":

    start_http_server(8001)

    monitor()