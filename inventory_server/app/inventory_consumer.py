from kafka import KafkaConsumer
import json
from config import curso

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
  except Exception as e:
      print(f"Error {e}")  

if __name__ == "__main__":
  kafka_event()