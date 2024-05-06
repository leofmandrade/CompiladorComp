from abc import abstractmethod
import sys
import re
# adicionar while, if, do, then, else, or, and, >, <, ==, read, not e end

arquivoSaida = "teste1.asm"


# classe que representa a tabela de símbolos
class SymbolTable():
    def __init__(self):
        self.table = {}
        self.words = ['print', 'if', 'then', 'else', 'while', 'do', 'and', 'or', 'not', 'read', 'end', 'local']
        self.count = 4
    
    def word(self, word):
        if word in self.words:
            return True
        else:
            return False

    def get(self, key):
        try:
            var = self.table[key]
            # print (f"MOV EAX, [EBP-{var[2]}];")
            WriteASM.write(f"MOV EAX, [EBP-{var[2]}];")
            # print(self.table[key])
            return var
        except:
            sys.stderr.write(f"Error: Undefined identifier '{key}'\n")
            sys.exit(1)
        
    def create(self, key, type):
        if key in self.table:
            sys.stderr.write(f"Error: Identifier '{key}' already defined\n")
            sys.exit(1)
        else:
            # print (f"PUSH DWORD 0;")
            WriteASM.write(f"PUSH DWORD 0;")
            self.table[key] = (None, type, self.count)
            self.count += 4

            # print(self.table[key], key)


    def set(self, key, value):
        if key not in self.table:
            sys.stderr.write(f"Error: Undefined identifier '{key}'\n")
            sys.exit(1)
        else:
            # print(f"MOV [EBP-{self.table[key][2]}], EAX;")
            WriteASM.write(f"MOV [EBP-{self.table[key][2]}], EAX;")
            self.table[key] = (value[0], int, self.table[key][2])

        
TabelaSimbolos = SymbolTable()


class WriteASM:
    output_contents = []
    filename = "teste1.asm"
    header_file = "header.asm"
    footer_file = "footer.asm"

    @staticmethod
    def write(line):
        WriteASM.output_contents.append(line + '\n')

    @staticmethod
    def set_filename(name):
        WriteASM.filename = name

    @staticmethod
    def dump():
        # Carrega e adiciona o header ao início do arquivo
        with open(WriteASM.header_file, 'r') as file:
            header = file.readlines()
            header.append('\n')  # Adiciona uma linha em branco após o header

        # Carrega e prepara o footer para ser adicionado ao final do arquivo
        with open(WriteASM.footer_file, 'r') as file:
            footer = file.readlines()
            footer.insert(0, '\n')  # Adiciona uma linha em branco antes do footer

        # Escreve o header, o conteúdo principal e o footer no arquivo
        with open(WriteASM.filename, 'w') as file:
            file.writelines(header + WriteASM.output_contents + footer)
        
        WriteASM.output_contents = []  # Limpa o buffer após escrever no arquivo



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
    id = 0
    def newId():
        t = Node.id
        Node.id += 1
        return t
    
    def __init__(self, value):
        self.value = value
        self.children = []
        self.id = Node.newId()

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

# integer value
class IntVal(Node):
    def Evaluate(self):
        valor = self.value
        # print (f"MOV EAX, {valor};")
        WriteASM.write(f"MOV EAX, {valor};")
        return (int(valor), int)
    

# classe de declaração de variável
class Assignment(Node):
    def Evaluate(self):
        TabelaSimbolos.set(self.children[0].value, self.children[1].Evaluate())


# classe de print
class Print(Node):
    def Evaluate(self):
        result = self.children[0].Evaluate()
        # print(f"PUSH EAX;")
        # print(f"PUSH formatout;")
        # print(f"CALL printf;")
        # print(f"ADD ESP, 8;")
        WriteASM.write(f"PUSH EAX;")
        WriteASM.write(f"PUSH formatout;")
        WriteASM.write(f"CALL printf;")
        WriteASM.write(f"ADD ESP, 8;")



# classe de identificador
class Identifier(Node):
    def Evaluate(self):
        # get type and value of the identifier
        return (TabelaSimbolos.get(self.value))

    

# binary operation (addition, subtraction, multiplication, division)
class BinOp(Node):
    def Evaluate(self):
        valor = self.value
        if valor == "+":
            child0 = self.children[1].Evaluate()
            # print(f"PUSH EAX;")
            WriteASM.write(f"PUSH EAX;")
            child1 = self.children[0].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"ADD EAX, EBX;")
            WriteASM.write(f"MOV EBX, EAX;")
            # print(f"POP EBX;")
            # print(f"ADD EAX, EBX;")
            # print(f"MOV EBX, EAX;")
            return (child0[0] + child1[0], int)
        elif valor == "-":
            child0 = self.children[1].Evaluate()
            WriteASM.write(f"PUSH EAX;")
            # print(f"PUSH EAX;")
            child1 = self.children[0].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"SUB EAX, EBX;")
            # print(f"POP EBX;")
            # print(f"SUB EAX, EBX;")
            return (child0[0] - child1[0], int)
        elif valor == "*":
            child0 = self.children[1].Evaluate()
            # print(f"PUSH EAX;")
            WriteASM.write(f"PUSH EAX;")
            child1 = self.children[0].Evaluate()
            # print(f"POP EBX;")
            # print(f"IMUL EBX;")
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"IMUL EBX;")
            return (child0[0] * child1[0], int)
        elif valor == "/":
            child0 = self.children[1].Evaluate()
            # print(f"PUSH EAX;")
            WriteASM.write(f"PUSH EAX;")
            child1 = self.children[0].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"IDIV EBX;")
            # print(f"POP EBX;")
            # print(f"IDIV EBX;")
            return (child0[0] // child1[0], int)
        elif valor == ">":
            child0 = self.children[0].Evaluate()
            # print(f"PUSH EAX;")
            WriteASM.write(f"PUSH EAX;")
            child1 = self.children[1].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"CMP EAX, EBX;")
            WriteASM.write(f"CALL binop_jg;")
            # print(f"POP EBX;")
            # print(f"CMP EAX, EBX;")
            # print(f"CALL binOpGT;")
            return (child0[0] > child1[0], int)
        elif valor == "<":
            child0 = self.children[0].Evaluate()
            WriteASM.write(f"PUSH EAX;")
            # print(f"PUSH EAX;")
            child1 = self.children[1].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"CMP EAX, EBX;")
            WriteASM.write(f"CALL binop_jl;")

            # print(f"POP EBX;")
            # print(f"CMP EAX, EBX;")
            # print(f"CALL binOpLT;")
            return (child0[0] < child1[0], int)
        elif valor == "==":
            child0 = self.children[1].Evaluate()
            # print(f"PUSH EAX;")
            WriteASM.write(f"PUSH EAX;")
            child1 = self.children[0].Evaluate()
            WriteASM.write(f"POP EBX;")
            WriteASM.write(f"CMP EAX, EBX;")
            WriteASM.write(f"CALL binop_je;")
            # print(f"POP EBX;")
            # print(f"CMP EAX, EBX;")
            # print(f"CALL binOpEQ;")
            return (child0[0] == child1[0], int)
        
class StrVal(Node):
    def Evaluate(self):
        return (self.value, str)

# unary operation (positive, negative)
class UnOp(Node):
    def Evaluate(self):
        valor = self.value
        if valor == "+":
            child = self.children[0].Evaluate()
            # print(f"MOV EAX, {child[0]};")
            WriteASM.write(f"MOV EAX, {child[0]};")
            return (child[0], int)
        elif valor == "-":
            child = self.children[0].Evaluate()
            WriteASM.write(f"MOV EAX, {child[0]};")
            WriteASM.write(f"NEG EAX;")
            # print(f"MOV EAX, {child[0]};")
            # print(f"NEG EAX;")
            return (-child[0], int)
        elif valor == "not":
            child = self.children[0].Evaluate()
            WriteASM.write(f"MOV EAX, {child[0]};")
            WriteASM.write(f"NOT EAX;")
            # print(f"MOV EAX, {child[0]};")
            # print(f"NOT EAX;")
            return (not child[0], int)
        

# no operation
class NoOp(Node):
    def Evaluate(self):
        pass

# while operation
class WhileOp(Node):
    def Evaluate(self):
        newId = self.id
        WriteASM.write("LOOP_{0}: ".format(newId))
        self.children[0].Evaluate()
        WriteASM.write(f"CMP EAX, False;")
        WriteASM.write("JE EXIT_{0}".format(newId))
        self.children[1].Evaluate()
        WriteASM.write("JMP LOOP_{0}".format(newId))
        WriteASM.write("EXIT_{0}: ".format(newId))
            

# var declaration
class VarDec(Node):
    # primeiro filho é o identificador, segundo é o valor, caso tenha. se nao tiver o segundo filho, o valor é none
    def Evaluate(self):

        if len(self.children) == 2:
            TabelaSimbolos.create(self.children[0].value, self.children[1].Evaluate()[1])
            TabelaSimbolos.set(self.children[0].value, self.children[1].Evaluate())
        else:
            TabelaSimbolos.create(self.children[0].value, None)        

# if operation
class IfOp(Node):
    def Evaluate(self):
        newId = self.id
        elseLabel = f"ELSE_{newId}"
        endLabel = f"END_IF_{newId}"


        self.children[0].Evaluate()
        WriteASM.write(f"CMP EAX, False;")
        WriteASM.write(f"JE {elseLabel};")
        self.children[1].Evaluate()
        WriteASM.write(f"JMP {endLabel};")
        WriteASM.write(f"ELSE_{newId}: ;")
        if len (self.children) == 3:
            self.children[2].Evaluate()
        WriteASM.write(f"{endLabel}: ;")





# função que le um valor
class Read(Node):
    # no sem filhos. sempre vai ler um int
    def Evaluate(self):
        # print(f"PUSH scanint;")
        # print(f"PUSH formatin;")
        # print(f"CALL scanf;")
        # print(f"ADD ESP, 8;")
        # print(f"MOV EAX, DWORD [scanint];")
        # print(f"MOV [EBP-{TabelaSimbolos.get(self.children[0].value)[2]}], EAX;")
        WriteASM.write(f"PUSH scanint;")
        WriteASM.write(f"PUSH formatin;")
        WriteASM.write(f"CALL scanf;")
        WriteASM.write(f"ADD ESP, 8;")
        WriteASM.write(f"MOV EAX, DWORD [scanint];")
        WriteASM.write(f"MOV [EBP-{TabelaSimbolos.get(self.children[0].value)[2]}], EAX;")
        
        return (int(input()), int)
    

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

        elif self.tokenizer.next.type == "IDENTIFIER":      #se for identificador, avança pro próximo token e chama parseBoolExpression()
            atual = self.tokenizer.next
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "ASSIGN":
                sys.stderr.write("Error: Expected '='")
                sys.exit(1)
            self.tokenizer.selectNext()
            result = Assignment("Assignment")
            result.children.append(Identifier(atual.value))
            result.children.append(self.parseBoolExpression())
            
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

            self.tokenizer.selectNext()
            if operation.type == "PLUS":
                node = BinOp("+")
            elif operation.type == "MINUS":
                node = BinOp("-")
            elif operation.type == "CONCAT":
                node = BinOp("..")
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
        
        elif operation.type == "STRING":    #se for string, avança pro próximo token e retorna o valor da string
            self.tokenizer.selectNext()
            return StrVal(operation.value)
        
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
    result = root_node.Evaluate()
    WriteASM.dump()

if __name__ == "__main__":
    # entrada é "main.py [arquivo]" 
    file = open(sys.argv[1], "r")
    code = file.read()
    file.close()
    #adicionar o header.asm no começo do saida.asm e o footer.asm no final
    
    (main(code))