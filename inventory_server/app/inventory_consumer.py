from kafka import KafkaConsumer
import json
from config import curso
import smtplib, ssl
from decouple import config



ORDER_KAFKA_TOPIC = "cart_details"

ORDER_CONFIRMED_KAFKA_TOPIC = "update_order_status_confirmed"


consumer = KafkaConsumer(
                        ORDER_KAFKA_TOPIC,
                        bootstrap_servers=['host.docker.internal:9300'],
                        api_version=(0,11,5)
                        )

def kafka_event():
  print("sending ","="*200,">>>>>>>>>>>>>>>>>>>>>>")
  try: 

    port = 465  # For SSL
    smtp_server = config('gmail.com')
    sender_email = config('gmail.com')  # Enter your address
      # Enter receiver address
    password = config("password")
    message = """
    Subject: Hi there

    Thank you for shopping with us. If you want 15% off your next order, leave a review on our website."""
    db = curso()
    c = db.cursor()
    for i in consumer:
       b = json.loads(i[6].decode())
       sqll = f"""
                           UPDATE inventory SET 
                           quantity = quantity - {int(b["units_sold"])}
                          where item_id = '{b["item_id"]}'

              """
       c.execute(sqll)
       db.commit()
       
       print(f" confirm quantity of <{b['item_id']}> check was send ","="*50,">>>>>>")
       receiver_email = b["email_customer"]
       context = ssl.create_default_context()
       with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        print(f"thank you email was sent to {receiver_email}")
  except Exception as e:
      print(f"Error {e}")  

if __name__ == "__main__":
  kafka_event()