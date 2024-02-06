import sys

def main(args):
    print(args)
    numAnterior = args[0]
    numPost = 0
    soma = '+'
    sub = '-'
    result = 0

    for i in range(len(args)):
        if args[i] == soma:
            numPost = args[i+1]
            result += int(numAnterior) + int(numPost)
        elif args[i] == sub:
            numPost = args[i+1]
            result += int(numAnterior) - int(numPost)
        numAnterior = numPost
    return result
    



if __name__ == "__main__":
    args = sys.argv[1:]
    print (main(args[0]))
