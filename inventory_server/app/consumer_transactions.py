from kafka import KafkaConsumer
import json
from config import curso

ORDER_KAFKA_TOPIC = "transactions_details"

ORDER_CONFIRMED_KAFKA_TOPIC = "ingredient_confirmed"


consumer = KafkaConsumer(
                        ORDER_KAFKA_TOPIC,
                        bootstrap_servers=['host.docker.internal:9300'],
                        api_version=(0,11,5)
                        )

def event_driver():
  print("sending ","="*200,">>>>>>>>>>>>>>>>>>>>>>")
  try: 
    db = curso()
    c = db.cursor()
    for i in consumer:
      print(i)
    #   b = json.loads(i[6].decode())
    #   a = json.loads(b)
    #   l = list(i for i in a )
    #   f = float(a["flour"])*int(a["quantity"])
    #   t = float(a["tomato sauce"])*int(a["quantity"])
    #   m = float(a["mozzarella"])*int(a["quantity"])
    #   x = float(a[l[3]])*int(a["quantity"])
    
    #   s = ()
    #   sqll = '''insert into transactions(orders_id,id_customer,
    #            payment_methods,order_status,
    #           total_prices,note)
    #           values(%s,%s,%s,%s,%s,%s) ;
    #           '''
    #   c.execute(sqll,s)
    #   db.commit()
  except Exception as e:
      print(f"Error {e}")  


event_driver()