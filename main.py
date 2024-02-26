import sys


class Token():
    def __init__(self, type, value):
        self.type = type                                    #tipo do token
        self.value = value                                  #valor do token

class Tokenizer():
    def __init__(self, source, position, next):
        self.source = source                                #código fonte a ser tokenizado
        self.position = position                                   #posição atual que o tokenizador está
        self.next = next                                    #ultimo token separado

    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1

        if self.position < len(self.source):
            if self.source[self.position] == "*":
                self.next = Token("TIMES", "*")
                self.position += 1
            elif self.source[self.position] == "/":
                self.next = Token("DIVIDE", "/")
                self.position += 1
            elif self.source[self.position] == "+":
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
        else:
            self.next = Token("EOF", "")

        return self.next

        
class Parser():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer        
    
    def parseTerm(self):
        self.tokenizer.selectNext()
        # print ("AAAA: ", self.tokenizer.next.type)
        if self.tokenizer.next.type == "NUMBER":
            result = self.tokenizer.next.value
            self.tokenizer.selectNext()
            
            if self.tokenizer.next.type == "NUMBER":
                sys.stderr.write("Error: Expected an operator between numbers\n")
                sys.exit(1)
            while self.tokenizer.next.type == "TIMES" or self.tokenizer.next.type == "DIVIDE":
                if self.tokenizer.next.type == "TIMES":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == "NUMBER":
                        result *= self.tokenizer.next.value
                    else:
                        sys.stderr.write("Error: Expected a number after '+'\n")
                        sys.exit(1)
                elif self.tokenizer.next.type == "DIVIDE":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == "NUMBER":
                        result /= self.tokenizer.next.value
                    else:
                        sys.stderr.write("Error: Expected a number after '-'\n")
                        sys.exit(1)
                self.tokenizer.selectNext()
            return result
        else:
            sys.stderr.write("Error: Expected a number at the beginning\n")
            sys.exit(1)


    def parseExpression(self):
        result = self.parseTerm()

        while self.tokenizer.next.type == "PLUS" or self.tokenizer.next.type == "MINUS":
            if self.tokenizer.next.type == "PLUS":
                result += self.parseTerm()
            elif self.tokenizer.next.type == "MINUS":
                result -= self.parseTerm()
            else:
                sys.stderr.write("Error: Expected '+' or '-'\n")
                sys.exit(1)

        return int(result)
    

    def run(code):
        tokenizer = Tokenizer(code, 0, None)
        parser = Parser(tokenizer)
        return parser.parseExpression()



def main(code):
    return Parser.run(code)


if __name__ == "__main__":
    args = sys.argv[1:]
    print (main(args[0]))
