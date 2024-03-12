from abc import abstractmethod
import sys
import re

# representa um token com um tipo e um valor
class Token():
    def __init__(self, type, value):
        self.type = type  
        self.value = value 


# classe que filtra comentarios
class PrePro():
    def filter(self, source):
        source = re.sub(r"--.*", "", source)    # tira tudo que vem à direita de "--"
        source = re.sub(r"\n", "", source)      # tira quebra de linha e substitui por nada
        return source
        

class Node():
    def __init__(self, value):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate():
        pass


# binary operation (addition, subtraction, multiplication, division)
class BinOp(Node):
    def Evaluate(self):
        valor = self.value
        child1 = self.children[0].Evaluate()
        child2 = self.children[1].Evaluate()

        if valor == "+":
            return child1 + child2
        elif valor == "-":
            return child1 - child2
        elif valor == "*":
            return child1 * child2
        elif valor == "/":
            return child1 // child2
        

# unary operation (positive, negative)
class UnOp(Node):
    def Evaluate(self):
        valor = self.value
        child = self.children[0].Evaluate()

        if valor == "+":
            return +child
        elif valor == "-":
            return -child
        
        
# integer value
class IntVal(Node):
    def Evaluate(self):
        valor = self.value
        return int(valor)
    
# no operation
class NoOp(Node):
    def Evaluate(self):
        pass



# converte uma sequência de caracteres em tokens
class Tokenizer():
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
class Parser():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def parseExpression(self):
        result = self.parseTerm()
        
        while self.tokenizer.next.type == "PLUS" or self.tokenizer.next.type == "MINUS":
            operation = self.tokenizer.next

            self.tokenizer.selectNext()
            if operation.type == "PLUS":
                node = BinOp("+")
            elif operation.type == "MINUS":
                node = BinOp("-")
            node.children.append(result)
            node.children.append(self.parseTerm())
            result = node

        return result



    def parseTerm(self):
        result = self.parseFactor()

        while self.tokenizer.next.type == "TIMES" or self.tokenizer.next.type == "DIVIDE":
            operation = self.tokenizer.next

            self.tokenizer.selectNext()
            if operation.type == "TIMES":
                node = BinOp("*")
                operation = self.tokenizer.next
            elif operation.type == "DIVIDE":
                node = BinOp("/")
            node.children.append(result)
            node.children.append(self.parseFactor())
            result = node
        return result

    def parseFactor(self):
        operation = self.tokenizer.next
        if operation.type == "NUMBER":      #se for número, avança pro próximo token e retorna o valor do número
            self.tokenizer.selectNext()
            return IntVal(operation.value)
        
        elif operation.type == "PLUS":      #se for adição, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            node = UnOp("+")
            node.children.append(self.parseFactor())
            return node
                
        elif operation.type == "MINUS":     #se for subtração, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            node = UnOp("-")
            node.children.append(self.parseFactor())
            return node
        
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
        prepro = PrePro()
        code = prepro.filter(code)
        tokenizer = Tokenizer(code, 0)
        parser = Parser(tokenizer)
        return parser.parseExpression()
    

def main(code):
    root_node = Parser.run(code)
    return root_node.Evaluate()

if __name__ == "__main__":
    # entrada é o arquivo "entrada.lua" contando que tem apenas 1 linha, sem \n
    entrada = open("entrada.lua", "r").read()
    print(main(entrada))

