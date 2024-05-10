from abc import abstractmethod
import sys
import re
# adicionar while, if, do, then, else, or, and, >, <, ==, read, not e end

# classe que representa a tabela de símbolos
class SymbolTable():
    def __init__(self):
        self.table = {}
    
    def get(self, key):
        try:
            return self.table[key]
        except:
            sys.stderr.write(f"Error: Undefined identifier '{key}'\n")
            sys.exit(1)
        
    def create(self, key):
        if key in self.table:
            sys.stderr.write(f"Error: Identifier '{key}' already defined\n")
            sys.exit(1)
        else:
            self.table[key] = (None, None)

    def set(self, key, value, tipo):
        if key not in self.table:
            sys.stderr.write(f"Error: Undefined identifier '{key}'\n")
            sys.exit(1)
        else:
            self.table[key] = (value, tipo)
        
class FuncTable():
    # getter e setter de funções (nome, node(self))
    def __init__(self):
        self.table = {}

    def get(self, key):
        try:
            return self.table[key]
        except:
            sys.stderr.write(f"Error: Undefined function '{key}'\n")
            sys.exit(1)

    def set(self, key, value):
        self.table[key] = value


TabelaFuncoes = FuncTable()

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
    def Evaluate(ST):
        pass


# classe que representa um bloco de código
class Block(Node):
    def __init__(self, value, children=None):
        super().__init__(value)
        if children is None:
            self.children = []
        else:
            self.children = children

    def Evaluate(self, ST):
        for child in self.children:
            if child.value == "Return":
                return child.Evaluate(ST)
            # print(child)
            child.Evaluate(ST)


# classe de declaração de função
class FuncDec(Node):
    def Evaluate(self, ST):
        TabelaFuncoes.set(self.value, self)


# classe de chamada de função
class FuncCall(Node):
    def Evaluate(self, ST):
        node = TabelaFuncoes.get(self.value)
        if len(node.children) - 2 == len(self.children):
            localST = SymbolTable()
            
            # print (node.children[0].value, "VALOR")
            # print (node.children[1].value, "VALOR")
            # print (node.children[2].value, "VALOR")
            # print (node.children[3].value, "VALOR")

            for i in range(1, len(node.children) - 1):
                localST.create(node.children[i].value)
                localST.set(node.children[i].value, self.children[i-1].Evaluate(ST)[0], self.children[i-1].Evaluate(ST)[1])
            return node.children[-1].Evaluate(localST)
        else:
            sys.stderr.write("Error: Unexpected number of arguments\n")
            sys.exit(1)


# classe de declaração de variável
class Assignment(Node):
    def Evaluate(self, ST):
        valor = self.children[1].Evaluate(ST)
        ST.set(self.children[0].value, valor[0], valor[1])


# classe de print
class Print(Node):
    def Evaluate(self, ST):
        result = self.children[0].Evaluate(ST)
        if result is not None:
            print(result[0])  # Make sure result is not None before accessing it
        else:
            sys.stderr.write("Error: Undefined identifier\n")
            sys.exit(1)


# classe de identificador
class Identifier(Node):
    def Evaluate(self, ST):
        # get type and value of the identifier
        return (ST.get(self.value))
    

# binary operation (addition, subtraction, multiplication, division)
class BinOp(Node):
    def Evaluate(self, ST):
        valor = self.value
        child1, type1 = self.children[0].Evaluate(ST)
        child2, type2 = self.children[1].Evaluate(ST)
        # print ("child1", child1, "type1", type1)
        # print ("child2", child2, "type2", type2)

        if valor == "..":
            res = str(child1) + str(child2)
            return (res, "str")
        
        elif type1 == "int" and type2 == "int":
            if valor == "+":
                res = child1 + child2
            elif valor == "-":
                res = child1 - child2
            elif valor == "*":
                res = child1 * child2
            elif valor == "/":
                res = child1 // child2
            elif valor == "or":
                res = child1 or child2
            elif valor == "and":
                res = int(child1 and child2)
            elif valor == ">":
                res = int(child1 > child2)
            elif valor == "<":
                res = int(child1 < child2)
            elif valor == "==":
                res = int(child1 == child2)
            else:
                sys.stderr.write("ASDError: Unexpected character\n")
                sys.exit(1)
            return (res, "int")
        
        elif type1 == "str" and type2 == "str":
            if valor == ">":
                res = child1 > child2
            elif valor == "<":
                res = child1 < child2
            elif valor == "==":
                res = child1 == child2
            else:
                sys.stderr.write("ASDError: Unexpected character\n")
                sys.exit(1)
            if res == True:
                res = 1
            else:
                res = 0
            return (res, "int")


class StrVal(Node):
    def Evaluate(self, ST):
        return (self.value, "str")

# unary operation (positive, negative)
class UnOp(Node):
    def Evaluate(self, ST):
        valor = self.value
        child, tipo = self.children[0].Evaluate(ST)

        if tipo != "int":
            sys.stderr.write("Error: Expected integer\n")
            sys.exit(1)

        if valor == "+":
            res = +child
            return (res, "int")
        elif valor == "-":
            res = -child
            return (res, "int")
        elif valor == "not":
            res = not child
            return (res, "int")
        
# integer value
class IntVal(Node):
    def Evaluate(self, ST):
        valor = self.value
        return (int(valor), "int")
    
# no operation
class NoOp(Node):
    def Evaluate(self, ST):
        pass

# while operation
class WhileOp(Node):
    def Evaluate(self, ST):
        while self.children[0].Evaluate(ST)[0]:
            for child in self.children[1].children:
                child.Evaluate(ST)

# var declaration
class VarDec(Node):
    # primeiro filho é o identificador, segundo é o valor, caso tenha. se nao tiver o segundo filho, o valor é none
    def Evaluate(self, ST):
        # print (self.children[0].value)
        # cria com create. caso tenha valor, seta o valor
        ST.create(self.children[0].value)
        if len(self.children) == 2:
            valor = self.children[1].Evaluate(ST)
            # print(valor)
            ST.set(self.children[0].value, valor[0], valor[1])

        # print("----------------")


class Return(Node):
    def Evaluate(self, ST):
        return self.children[0].Evaluate(ST)


# if operation
class IfOp(Node):
    def Evaluate(self, ST):
        condicao = self.children[0].Evaluate(ST)
        if condicao:
            for child in self.children[1].children:
                child.Evaluate(ST)
        else:
            for child in self.children[2].children:
                child.Evaluate(ST)

# função que le um valor
class Read(Node):
    # no sem filhos. sempre vai ler um int
    def Evaluate(self, ST):
        return (int(input()), "int")
    

# converte uma sequência de caracteres em tokens
class Tokenizer():
    def __init__(self, source, position):
        self.source = source
        self.position = position
        self.next = self.selectNext()

    
    def selectNext(self):
        selectedWords = ['print', 'if', 'then', 'else', 'while', 'do', 'and', 'or', 'not', 'read', 'end', 'local', 'function', 'return']

        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1
        
        if self.position == len(self.source):       # se atingir o final da entrada, retorna um token de fim de arquivo (EOF)
            self.next = Token("EOF", "EOF")
        elif self.source[self.position] == ",":
            self.next = Token("COMMA", ",")
            self.position += 1
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
            if identifier in selectedWords:
                self.next = Token(identifier.upper(), identifier)
            else:
                self.next = Token("IDENTIFIER", identifier)

        elif self.source[self.position].isdigit():      #tokeniza número
            number = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                number += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", int(number))

        elif self.source[self.position] == " " or self.source[self.position] == "\t":     #ignora espaços e tabs e chama selectNext() novamente
            self.position += 1
            self.selectNext()
        
        # adiciona .. (concat) e string (acha " e tem que achar o  " de novo, se não achar, erro)
        elif self.source[self.position] == ".":
            if self.source[self.position + 1] == ".":
                self.next = Token("CONCAT", "..")
                self.position += 2
            else:
                sys.stderr.write(f"Error: Unexpected character '.'\n")
                sys.exit(1)
        
        elif self.source[self.position] == "\"":
            string = ""
            self.position += 1
            while self.position < len(self.source) and self.source[self.position] != "\"":
                string += self.source[self.position]
                self.position += 1
            if self.position == len(self.source):
                sys.stderr.write(f"Error: Expected '\"'\n")
                sys.exit(1)
            self.next = Token("STRING", string)
            self.position += 1
        
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
            lista.append(self.parseStatement())
        return Block("Block", lista)
    
     # function que analisa uma declaração
    def parseStatement(self):
        if self.tokenizer.next.type == "PRINT":       #se for print, avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()

            result = Print("Print")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "RPAREN":
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)
            self.tokenizer.selectNext()


        elif self.tokenizer.next.type == "FUNCTION":    
            # function, depois identifier
            # depois ( . depois pode ir pro identifier ou pra ). se for pro identifier ou vai pra virgula ou ). 
            # depois \n, ai pode chamar o parseStatement. depois end e \n
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "IDENTIFIER":
                sys.stderr.write("Error: Expected identifier")
                sys.exit(1)
            result = FuncDec(self.tokenizer.next.value)
            result.children.append(Identifier((self.tokenizer.next.value)))

            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()

            while self.tokenizer.next.type != "RPAREN":
                if self.tokenizer.next.type != "IDENTIFIER":
                    sys.stderr.write("Error: Expected identifier")
                    sys.exit(1)
                result.children.append(Identifier(self.tokenizer.next.value))
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "COMMA":
                    self.tokenizer.selectNext()

            if self.tokenizer.next.type != "RPAREN":
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)
            self.tokenizer.selectNext()

            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()

            bloco = Block("Block")
            while self.tokenizer.next.type != "END" and self.tokenizer.next.type != "EOF":
                bloco.children.append(self.parseStatement())
            if self.tokenizer.next.type == "EOF":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            result.children.append(bloco)
            if self.tokenizer.next.type != "END":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "SKIPLINE" and self.tokenizer.next.type != "EOF":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)

        elif self.tokenizer.next.type == "RETURN":
            # chama o parseBoolExpression 
            self.tokenizer.selectNext()
            result = Return("Return")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()


        elif self.tokenizer.next.type == "IDENTIFIER":      #se for identificador, avança pro próximo token e chama parseBoolExpression()
            ident = Identifier(self.tokenizer.next.value)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "ASSIGN":
                
                self.tokenizer.selectNext()
                result = Assignment("Assignment")
                result.children.append(ident)
                result.children.append(self.parseBoolExpression())
            elif self.tokenizer.next.type == "LPAREN":
                self.tokenizer.selectNext()
                result = FuncCall(ident.value)
                
                if self.tokenizer.next.type != "RPAREN":
                    result.children.append(self.parseBoolExpression())
                    while self.tokenizer.next.type == "COMMA":
                        self.tokenizer.selectNext()
                        result.children.append(self.parseBoolExpression())
                if self.tokenizer.next.type != "RPAREN":
                    sys.stderr.write("Error: Expected ')'")
                    sys.exit(1)
                self.tokenizer.selectNext()
            else:
                sys.stderr.write("Error: Unexpected character\n")
                sys.exit(1)

        elif self.tokenizer.next.type == "LOCAL":       #se for local, avança pro próximo token e chama parseStatement()
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "IDENTIFIER":
                sys.stderr.write("Error: Expected identifier")
                sys.exit(1)
            result = VarDec("VarDec")
            result.children.append(Identifier(self.tokenizer.next.value))
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "ASSIGN":
                self.tokenizer.selectNext()
                result.children.append(self.parseBoolExpression())


        elif self.tokenizer.next.type == "WHILE":       #se for while, avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            result = WhileOp("WhileOp")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "DO":
                sys.stderr.write("Error: Expected 'do'")
                sys.exit(1)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()
            bloco = Block("Block")

            while self.tokenizer.next.type != "END" and self.tokenizer.next.type != "EOF":
                bloco.children.append(self.parseStatement())
            if self.tokenizer.next.type == "EOF":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            result.children.append(bloco)
            if self.tokenizer.next.type != "END":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "SKIPLINE" and self.tokenizer.next.type != "EOF":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
                

        elif self.tokenizer.next.type == "IF":          #se for if, avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            result = IfOp("IfOp")
            result.children.append(self.parseBoolExpression())
            if self.tokenizer.next.type != "THEN":
                sys.stderr.write("Error: Expected 'then'")
                sys.exit(1)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "SKIPLINE":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)
            self.tokenizer.selectNext()
            bloco1 = Block("Block")
            while self.tokenizer.next.type != "ELSE" and self.tokenizer.next.type != "END" and self.tokenizer.next.type != "EOF":
                bloco1.children.append(self.parseStatement())
            if self.tokenizer.next.type == "EOF":
                sys.stderr.write("Error: Expected 'else' or 'end'")
                sys.exit(1)
            result.children.append(bloco1)
            if self.tokenizer.next.type == "ELSE":
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != "SKIPLINE":
                    sys.stderr.write("Error: Expected newline")
                    sys.exit(1)
                self.tokenizer.selectNext()
                bloco2 = Block("Block")
                while self.tokenizer.next.type != "END" and self.tokenizer.next.type != "EOF":
                    bloco2.children.append(self.parseStatement())
                if self.tokenizer.next.type == "EOF":
                    sys.stderr.write("Error: Expected 'end'")
                    sys.exit(1)
                result.children.append(bloco2)
                
            if self.tokenizer.next.type != "END":
                sys.stderr.write("Error: Expected 'end'")
                sys.exit(1)
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "SKIPLINE" and self.tokenizer.next.type != "EOF":
                sys.stderr.write("Error: Expected newline")
                sys.exit(1)


        elif self.tokenizer.next.type == "SKIPLINE":    #se for \n, avança pro próximo token
            self.tokenizer.selectNext()
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
        while self.tokenizer.next.type == "PLUS" or self.tokenizer.next.type == "MINUS" or self.tokenizer.next.type == "CONCAT":
            operation = self.tokenizer.next
            if operation.type == "PLUS":
                node = BinOp("+")
            elif operation.type == "MINUS":
                node = BinOp("-")
            elif operation.type == "CONCAT":
                node = BinOp("..")
            node.children.append(result)
            self.tokenizer.selectNext()
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
        
        elif operation.type == "STRING":    #se for string, avança pro próximo token e retorna o valor da string
            self.tokenizer.selectNext()
            return StrVal(operation.value)
        
        elif operation.type == "IDENTIFIER":   
            ident = Identifier(self.tokenizer.next.value)

            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "LPAREN":
                self.tokenizer.selectNext()
                result = FuncCall(ident.value)
                while self.tokenizer.next.type != "RPAREN":
                    result.children.append(self.parseBoolExpression())
                    if self.tokenizer.next.type == "COMMA":
                        self.tokenizer.selectNext()
                if self.tokenizer.next.type != "RPAREN":
                    sys.stderr.write("Error: Expected ')'")
                    sys.exit(1)
                self.tokenizer.selectNext()
            else:
                result = Identifier(operation.value)
            return result
        
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
        
        elif operation.type == "NOT":       #se for not, avança pro próximo token e chama parseFactor()
            self.tokenizer.selectNext()
            node = UnOp("not")
            node.children.append(self.parseFactor())
            return node
        
        elif operation.type == "LPAREN":    #se for ( avança pro próximo token e chama parseBoolExpression()
            self.tokenizer.selectNext()
            result = self.parseBoolExpression()
            if self.tokenizer.next.type == "RPAREN":    #se for ) avança para o próximo token
                self.tokenizer.selectNext()
                return result
            else:
                sys.stderr.write("Error: Expected ')'\n")
                sys.exit(1)

        elif operation.type == "READ":      #se for read, avanca pro próximo token, ve se tem "(". avanca pro proximo e chama o read. ve se tem ")" no final
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "LPAREN":
                sys.stderr.write("Error: Expected '('")
                sys.exit(1)
            self.tokenizer.selectNext()
            result = Read("Read")
            if self.tokenizer.next.type == "RPAREN":
                self.tokenizer.selectNext()
                return result
            else:
                sys.stderr.write("Error: Expected ')'")
                sys.exit(1)


        else:
            sys.stderr.write("Error: Expected number or '(', received "+ operation.value)
            sys.exit(1)

    
   



    def run(code):
        code = PrePro().filter(code)

        tokenizer = Tokenizer(code, 0)
        # while tokenizer.next.type != "EOF":
        #     tokenizer.selectNext()

        parser = Parser(tokenizer)
        result = parser.parseBlock()
    
        if tokenizer.next.type != "EOF":
            sys.stderr.write("Error: Unexpected character\n")
            sys.exit(1)

        return result





def main(code):
    root_node = Parser.run(code)
    ST = SymbolTable()
    return root_node.Evaluate(ST)

if __name__ == "__main__":
    # entrada é "main.py [arquivo]" 
    file = open(sys.argv[1], "r")
    code = file.read()
    file.close()
    (main(code))
