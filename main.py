from abc import abstractmethod
import sys
import re
# adicionar while, if, do, then, else, or, and, >, <, ==, read, not e end

# classe que representa a tabela de símbolos
class SymbolTable():
    def __init__(self):
        self.table = {}
        self.words = ['print', 'if', 'then', 'else', 'while', 'do', 'and', 'or', 'not', 'read', 'end']

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
        elif valor == ">":
            return child1 > child2
        elif valor == "<":
            return child1 < child2
        elif valor == "==":
            return child1 == child2
        elif valor == "or":
            return child1 or child2
        elif valor == "and":
            return child1 and child2

# unary operation (positive, negative)
class UnOp(Node):
    def Evaluate(self):
        valor = self.value
        child = self.children[0].Evaluate()

        if valor == "+":
            return +child
        elif valor == "-":
            return -child
        elif valor == "not":
            return not child
        
# integer value
class IntVal(Node):
    def Evaluate(self):
        valor = self.value
        return int(valor)
    
# no operation
class NoOp(Node):
    def Evaluate(self):
        pass

# while operation
class WhileOp(Node):
    def Evaluate(self):
        while self.children[0].Evaluate():
            self.children[1].Evaluate()


# if operation
class IfOp(Node):
    def Evaluate(self):
        if self.children[0].Evaluate():
            self.children[1].Evaluate()
        else:
            self.children[2].Evaluate()

# função que le um valor
class Read(Node):
    # no sem filhos. sempre vai ler um int
    def Evaluate(self):
        return int(input())
    

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
            if self.source[self.position + 1] == "=":
                self.next = Token("EQUALS", "==")
                self.position += 2
            else:
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
                self.next = Token(identifier.upper(), identifier)
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
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)

        
        elif self.source[self.position] == ">":
            self.next = Token("GT", ">")
            self.position += 1

        elif self.source[self.position] == "<":
            self.next = Token("LT", "<")
            self.position += 1
        else:
            sys.stderr.write(f"Error: Unexpected character '{self.source[self.position]}'\n")
            sys.exit(1)
        return self.next

# análise sintática da expressão
class Parser():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    # function que analisa um bloco de código
    def parseBlock(self):
        lista = []
        while self.tokenizer.next.type != "EOF":
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            lista.append(self.parseStatement())
        return Block("Block", lista)
    
     # function que analisa uma declaração
    def parseStatement(self):
        if self.tokenizer.next.type == "PRINT":       #se for print, avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)

            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)

            result = Print("Print")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "RPAREN":
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)



        elif self.tokenizer.next.type == "IDENTIFIER":      #se for identificador, avança pro próximo token e chama parseBoolExpression()
            atual = self.tokenizer.next
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "ASSIGN":
                sys.stderr.write("Error: Expected '='")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = Assignment("Assignment")
            result.children.append(Identifier(atual.value))
            result.children.append(self.parseBoolExpression())

        elif self.tokenizer.next.type == "WHILE":
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = WhileOp("WhileOp")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "DO":
                sys.stderr.write("Error: Expected 'do'")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result.children.append(self.parseBlock())
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "END":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            

        elif self.tokenizer.next.type == "IF":
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = IfOp("IfOp")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "THEN":
                sys.stderr.write("Error: Expected 'then'")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result.children.append(self.parseBlock())
            if self.tokenizer.next.type == "ELSE":
                self.tokenizer.selectNext()
                print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
                if self.tokenizer.next.type != "SKIPLINE":
                    sys.stderr.write("Error: Expected newline")
                    sys.exit(1)
                self.tokenizer.selectNext()
                print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
                result.children.append(self.parseBlock())
            else:
                result.children.append(NoOp("NoOp"))
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "END":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
                
        elif self.tokenizer.next.type == "SKIPLINE":    #se for \n, avança pro próximo token
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = NoOp("NoOp")

        else:
            sys.stderr.write("Error: Expected identifier, 'print' or newline")
            sys.exit(1)
        return result
    
    # function que analisa boolean expression
    def parseBoolExpression(self):
        result = self.parseBoolTerm()
        while self.tokenizer.next.type == "OR":
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            node = BinOp("or")
            node.children.append(result)
            node.children.append(self.parseBoolTerm())
            result = node
        return result
    
    # function que analisa boolean term
    def parseBoolTerm(self):
        result = self.parseRelationalExpression()
        while self.tokenizer.next.type == "AND":
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            node = BinOp("and")
            node.children.append(result)
            node.children.append(self.parseRelationalExpression())
            result = node
        return result
    
    # function que analisa relational expression
    def parseRelationalExpression(self):
        result = self.parseExpression()
        while self.tokenizer.next.type == "GT" or self.tokenizer.next.type == "LT" or self.tokenizer.next.type == "EQUALS":
            operation = self.tokenizer.next
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if operation.type == "GT":
                node = BinOp(">")
            elif operation.type == "LT":
                node = BinOp("<")
            elif operation.type == "EQUALS":
                node = BinOp("==")
            node.children.append(result)
            node.children.append(self.parseExpression())
            result = node
        return result


    # function que inicia a análise sintática
    def parseExpression(self):
        result = self.parseTerm()
        while self.tokenizer.next.type == "PLUS" or self.tokenizer.next.type == "MINUS":
            operation = self.tokenizer.next

            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
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
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
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
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            return IntVal(operation.value)
        
        elif operation.type == "IDENTIFIER":    #se for identificador, avança pro próximo token e retorna o valor do identificador
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            return Identifier(operation.value)
        
        elif operation.type == "PLUS":      #se for adição, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            node = UnOp("+")
            node.children.append(self.parseFactor())
            return node
                
        elif operation.type == "MINUS":     #se for subtração, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            node = UnOp("-")
            node.children.append(self.parseFactor())
            return node
        
        elif operation.type == "NOT":       #se for not, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            node = UnOp("not")
            node.children.append(self.parseFactor())
            return node
        
        elif operation.type == "LPAREN":    #se for ( avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = self.parseBoolExpression()
            if self.tokenizer.next.type == "RPAREN":    #se for ) avança para o próximo token
                self.tokenizer.selectNext()
                print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
                return result
            else:
                sys.stderr.write("Error: Expected ')'\n")
                sys.exit(1)

        elif operation.type == "READ":      #se for read, avanca pro próximo token, ve se tem "(". avanca pro proximo e chama o read. ve se tem ")" no final
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()
            print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
            result = Read("Read")
            if self.tokenizer.next.type == "RPAREN":
                self.tokenizer.selectNext()
                print("type: ", self.tokenizer.next.type, "value: ", self.tokenizer.next.value)
                return result
            else:
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)

        else:
            sys.stderr.write("Error: Expected number or '('")
            sys.exit(1)



    
   



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
