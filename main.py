import sys

# representa um token com um tipo e um valor
class Token:
    def __init__(self, type, value):
        self.type = type  
        self.value = value 



# converte uma sequência de caracteres em tokens
class Tokenizer:
    def __init__(self, source, position):
        self.source = source
        self.position = position
        self.next = self.selectNext()
    
    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1
        
        if self.position == len(self.source):       # se atingir o final da entrada, retorna um token de fim de arquivo (EOF)
            self.next = Token("EOF", "EOF")

        elif self.source[self.position] == "(":
            self.next = Token("LPAREN", "(")
            self.position += 1
        elif self.source[self.position] == ")":
            self.next = Token("RPAREN", ")")
            self.position += 1
        elif self.source[self.position] == "+":
            self.next = Token("PLUS", "+")
            self.position += 1
        elif self.source[self.position] == "-":
            self.next = Token("MINUS","-")
            self.position += 1
        elif self.source[self.position] == "*":
            self.next = Token("TIMES", "*")
            self.position += 1
        elif self.source[self.position] == "/":
            self.next = Token("DIVIDE", "/")
            self.position += 1


        elif self.source[self.position].isdigit():      #tokeniza número
            number = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                number += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", int(number))
            
        
        elif self.source[self.position] == " ":         #ignora espaços em branco e chama recursivamente selectNext()
            self.position += 1
            self.selectNext()
        else:
            sys.stderr.write(f"Error: Unexpected character '{self.source[self.position]}'\n")
            sys.exit(1)
        return self.next


# análise sintática da expressão
class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def parseExpression(self):
        result = self.parseTerm()
        operation = self.tokenizer.next
        
        while operation.type == "PLUS" or operation.type == "MINUS":
            self.tokenizer.selectNext()
            if operation.type == "PLUS":
                result += self.parseTerm()
            elif operation.type == "MINUS":
                result -= self.parseTerm()
            operation = self.tokenizer.next
            if operation.type == "NUMBER":
                sys.stderr.write("Error: Expected '+' or '-'\n")
                sys.exit(1)
        return result

    def parseTerm(self):
        result = self.parseFactor()
        operation = self.tokenizer.next

        while operation.type == "TIMES" or operation.type == "DIVIDE":
            self.tokenizer.selectNext()
            if operation.type == "TIMES":
                result *= self.parseFactor()
                operation = self.tokenizer.next
            elif operation.type == "DIVIDE":
                result //= self.parseFactor()
                operation = self.tokenizer.next
        return result

    def parseFactor(self):
        operation = self.tokenizer.next
        if operation.type == "NUMBER":      #se for número, avança pro próximo token e retorna o valor do número
            self.tokenizer.selectNext()
            return operation.value
        
        elif operation.type == "PLUS":      #se for adição, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            return self.parseFactor()
        
        elif operation.type == "MINUS":     #se for subtração, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            return -self.parseFactor()
        
        elif operation.type == "LPAREN":    #se for ( avança pro próximo token e chama parseExpression()
            self.tokenizer.selectNext()
            result = self.parseExpression()
            if self.tokenizer.next.type == "RPAREN":    #se for ) avança para o próximo token
                self.tokenizer.selectNext()
                return result
            else:
                sys.stderr.write("Error: Expected ')'\n")
                sys.exit(1)
        else:
            sys.stderr.write("Error: Expected number or '('")
            sys.exit(1)


    def run(code):
        tokenizer = Tokenizer(code, 0)
        parser = Parser(tokenizer)
        result = parser.parseExpression()
        if tokenizer.next.type != "EOF":        #exibe erro se houverem caracteres não consumidos após a análise
            sys.stderr.write("Error: Unexpected character\n")
            sys.exit(1)
        return result

def main(code):
    return Parser.run(code)

if __name__ == "__main__":
    args = sys.argv[1:]
    print(main(args[0]))