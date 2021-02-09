from kafka import KafkaConsumer as kc

bootstrap_servers = ["220.69.209.21%d:9092"%d for d in range(3)]

print("안녕")
consumer = kc("BG",bootstrap_servers=bootstrap_servers,auto_offset_reset='earliest',group_id="1234")
getsData = []
for i in consumer:
    print((i.value).decode("utf8")) # getsData 에 append
    if (len(getsData)>10):
        #학습
        getsData = []