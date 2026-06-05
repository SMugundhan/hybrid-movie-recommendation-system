import redis

r = redis.Redis ( host = "localhost", port = 6379, decode_responses = True ) 

r.set ( "name", "Mugundhan", ex = 10 )

value = r.get ( "name" )

print ( value )




# By default, Redis stores and returns raw bytes. For example, if you set a key "name" with value "Mugundhan", retrieving it might give you b'Mugundhan' # (a bytes object in Python).


# Use decode_responses=True when you’re only dealing with textual data (strings, JSON, etc.).

# Use decode_responses=False when you need to store binary data safely
