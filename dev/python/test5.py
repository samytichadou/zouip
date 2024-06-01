from urllib.parse import unquote

us = r"/home/tonton/Desktop/r%C3%A9cap%20normaal%20juillet%202023"
print(us)

test = unquote(us)
print(test)
