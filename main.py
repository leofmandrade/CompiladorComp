import sys


class Token():
    def __init__(self, type, value):
        self.type = type                                    #tipo do token
        self.value = value                                  #valor do token

class Tokenizer():
    def __init__(self, source):
        self.source = source                                #código fonte a ser tokenizado
        self.position = 0                                   #posição atual que o tokenizador está
        self.next = None                                    #ultimo token separado

    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1

        if self.position < len(self.source):
            if self.source[self.position] == "+":
                self.next = Token("PLUS", "+")
                self.position += 1
            elif self.source[self.position] == "-":
                self.next = Token("MINUS", "-")
                self.position += 1
            elif self.source[self.position].isdigit():
                number = ""
                while self.position < len(self.source) and self.source[self.position].isdigit():
                    number += self.source[self.position]
                    self.position += 1
                self.next = Token("NUMBER", int(number))
            return self.next
        else:
            return Token("EOF", "")
        
class Parser():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer        
    
    def parseExpression(self):
        self.tokenizer.selectNext()
        
        if self.tokenizer.next.type == "NUMBER":
            result = self.tokenizer.next.value
            self.tokenizer.selectNext()
            while self.tokenizer.next.type == "PLUS" or self.tokenizer.next.type == "MINUS":
                if self.tokenizer.next.type == "PLUS":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == "NUMBER":
                        result += self.tokenizer.next.value
                    else:
                        sys.stderr.write("Error: Expected a number after '+'\n")
                        sys.exit(1)
                elif self.tokenizer.next.type == "MINUS":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == "NUMBER":
                        result -= self.tokenizer.next.value
                    else:
                        sys.stderr.write("Error: Expected a number after '-'\n")
                        sys.exit(1)
                self.tokenizer.selectNext()
            return result
        else:
            sys.stderr.write("Error: Expected a number at the beginning\n")
            sys.exit(1)

    def run(code):
        tokenizer = Tokenizer(code)
        parser = Parser(tokenizer)
        return parser.parseExpression()



def main(code):
    return Parser.run(code)


if __name__ == "__main__":
    args = sys.argv[1:]
    print (main(args[0]))
