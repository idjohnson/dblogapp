import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Replace with your connection string or set as env var
CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR", "Endpoint=sb://daprpubsubdemo1.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_KEY")
QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME", "logingest")

# Example message body (can be any string, or JSON if you want to parse it in your app)
body = "This is a test log message from CLI!"

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        message = ServiceBusMessage(body)
        sender.send_messages(message)
        print(f"Sent message: {body}")
