import sys

def main(args):
    listaNumeros = []
    listaOperacao = []
    numero = ''

    for i in args:
        if i != '+' and i != '-':
            numero += i
        elif i == '+' or i == '-':
            listaNumeros.append(int(numero))
            listaOperacao.append(i)
            numero = ''  

    listaNumeros.append(int(numero))
    # print (listaNumeros)


    resultado = 0
    for i in range(len(listaNumeros)):
        if i == 0:
            resultado = listaNumeros[i]
        else:
            if listaOperacao[i-1] == '+':
                resultado += listaNumeros[i]
            else:
                resultado -= listaNumeros[i]

    return resultado


if __name__ == "__main__":
    args = sys.argv[1:]
    print (main(args[0]))
