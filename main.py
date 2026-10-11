from lexer import Lexer


source = """
start:
x = 5
if x >= 3 goto attack_enemy
say("hello")
# comentario
"""


lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)