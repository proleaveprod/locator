import re
message = b'r100f11;'
str_message=str(message)
print(message)

data  = re.findall(r'\d+',str(str_message.partition(';')[0]))

print("data0:",data[0])


