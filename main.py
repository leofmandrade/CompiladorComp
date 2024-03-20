from abc import abstractmethod
import sys
import re

# classe que representa a tabela de símbolos
class SymbolTable():
    def __init__(self):
        self.table = {}
        self.words = ['print']

    def get(self, key):
        try:
            return self.table[key]
        except:
            sys.stderr.write(f"Error: Undefined identifier '{key}'\n")
            sys.exit(1)
    
    def word(self, word):
        if word in self.words:
            return True
        else:
            return False


    def set(self, key, value):
        self.table[key] = value
        
TabelaSimbolos = SymbolTable()


# representa um token com um tipo e um valor
class Token():
    def __init__(self, type, value):
        self.type = type  
        self.value = value 


# classe que filtra comentarios
class PrePro():
    def filter(self, source):
        # remove comentarios em lua
        source = re.sub(r'--.*', ' ', source)
        return source
        

# classe que representa um nó da árvore de sintaxe abstrata
class Node():
    def __init__(self, value):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate():
        pass

# classe que representa um bloco de código
class Block(Node):
    def __init__(self, value, children=None):
        super().__init__(value)
        if children is None:
            self.children = []
        else:
            self.children = children

    def Evaluate(self):
        for child in self.children:
            child.Evaluate()



# classe de declaração de variável
class Assignment(Node):
    def Evaluate(self):
        TabelaSimbolos.set(self.children[0].value, self.children[1].Evaluate())


# classe de print
class Print(Node):
    def Evaluate(self):
        print(self.children[0].Evaluate())


# classe de identificador
class Identifier(Node):
    def Evaluate(self):
        return TabelaSimbolos.get(self.value)
    

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
        elif self.source[self.position] == "=":
            self.next = Token("ASSIGN", "=")
            self.position += 1
        elif self.source[self.position] == "\n":
            self.next = Token("SKIPLINE", "SKIPLINE")
            self.position += 1

        elif self.source[self.position].isalpha():       #tokeniza identificador
            identifier = self.source[self.position]
            self.position += 1
            while self.position < len(self.source) and (self.source[self.position].isalpha() or self.source[self.position].isdigit() or self.source[self.position] == "_"):
                identifier += self.source[self.position]
                self.position += 1
            if TabelaSimbolos.word(identifier):
                self.next = Token("PRINT", identifier)
            else:
                self.next = Token("IDENTIFIER", identifier)

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

    # function que inicia a análise sintática
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

    # function que analisa um termo
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

    # function que analisa um fator
    def parseFactor(self):
        operation = self.tokenizer.next
        if operation.type == "NUMBER":      #se for número, avança pro próximo token e retorna o valor do número
            self.tokenizer.selectNext()
            return IntVal(operation.value)
        
        elif operation.type == "IDENTIFIER":    #se for identificador, avança pro próximo token e retorna o valor do identificador
            self.tokenizer.selectNext()
            return Identifier(operation.value)
        
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


    # function que analisa um bloco de código
    def parseBlock(self):
        lista = []
        while self.tokenizer.next.type != "EOF":
            lista.append(self.parseStatement())
        return Block("Block", lista)
    
    
    # function que analisa uma declaração
    def parseStatement(self):
        if self.tokenizer.next.type == "IDENTIFIER":      #se for identificador, avança pro próximo token e chama parseExpression()
            atual = self.tokenizer.next
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "ASSIGN":
                sys.stderr.write("Error: Expected '='")
                sys.exit(1)
            self.tokenizer.selectNext()
            result = Assignment("Assignment")
            result.children.append(Identifier(atual.value))
            result.children.append(self.parseExpression())

        elif self.tokenizer.next.type == "PRINT":       #se for print, avança pro próximo token e chama parseExpression()
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()
            result = Print("Print")
            result.children.append(self.parseExpression())
            if self.tokenizer.next.type != "RPAREN":
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)
            self.tokenizer.selectNext()

        elif self.tokenizer.next.type == "SKIPLINE":    #se for \n, avança pro próximo token
            self.tokenizer.selectNext()
            result = NoOp("NoOp")
            
        else:
            sys.stderr.write("Error: Expected identifier, 'print' or newline")
            sys.exit(1)
        return result



    def run(code):
        code = PrePro().filter(code)
        # print("Filtered code:", code)

        tokenizer = Tokenizer(code, 0)
        
        # print("Tokenizer initialized")
        # print("Tokens:")
        # while tokenizer.next.type != "EOF":
        #     print(tokenizer.next.value)
        #     tokenizer.selectNext()

        parser = Parser(tokenizer)
        result = parser.parseBlock()


        if tokenizer.next.type != "EOF":
            sys.stderr.write("Error: Unexpected character\n")
            sys.exit(1)
        return result





def main(code):
    root_node = Parser.run(code)
    return root_node.Evaluate()

if __name__ == "__main__":
    # entrada é "main.py [arquivo]" 
    file = open(sys.argv[1], "r")
    code = file.read()
    file.close()
    (main(code))
