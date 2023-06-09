a = {"a" : 1,
     "b" : 2,
     "c" : 3}
# print(a)

# if "d" not in a:
#     print(a["b"])
# else:
#     print("dosen't exist")    

# if "c" not in a:
#      raise a["a"]
# else:
#      print("dosen't exist")

try :
    try:
        if "d" not in a:
            print("something")
            raise Exception("0")  # 1
        else:
            print("dosen't exist")
    except :
            print("testing")
  
     
except :
    print("erro")    