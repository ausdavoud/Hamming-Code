import random
from copy import deepcopy
import math
import numpy as np
from scipy.optimize import root_scalar
from numpy import random as num_random


def NewSort(L):
    n = len(L)
    member = L[n-1]
    for i in range(n):
        if member[0] >= L[i][0]:
            L.pop(n-1)
            L.insert(i, member)
            break
    return L


def UpdateB(L, B):
    n = len(L)
    for i in range(n-2):
        for set_member in L[i][1]:
            B[set_member] = " " + B[set_member]
    
    for set_member in L[n-2][1]:
            B[set_member] = "0" + B[set_member]        

    for set_member in L[n-1][1]:
            B[set_member] = "1" + B[set_member]                
    
    return B       


def Huffman(P):
    P.sort(reverse=True)
    n = len(P)

    T = [[]] * n
    for i in range(n):
        T[i] = [P[i], {i}]

    B = [""] * n

    while (len(T)!= 1):
        B = UpdateB(T, B)

        m = len(T)
        new_p = T[m-2][0] + T[m-1][0]
        new_set = T[m-2][1].union(T[m-1][1])
        T.pop(m-1)
        T.pop(m-2)
        T.append([new_p, new_set])

        T = NewSort(T)

    for i in range(len(B)):
        B[i] = B[i].replace(" ", "")

    return B


def IncodeByHuffman(String, Language):
    Posibility = []
    for l in Language:
        Posibility.append(l[1])

    CodeWords = Huffman(Posibility)

    AlphabetDict = {}
    for i in range(len(Language)):
        AlphabetDict[Language[i][0]] = CodeWords[i]    

    for l, code in AlphabetDict.items():
        String = String.replace(l, code)

    return String, AlphabetDict

def GenerateRandomSourceString(source, length):
    s_alphabet = []
    s_possibillities = []
    for s in source:
        s_alphabet.append(s[0])
        s_possibillities.append(s[1])

    string = ""
    ListChar = random.choices(s_alphabet, s_possibillities, k=length)
    for char in ListChar:
        string += char
    return string    




     

def BuildMatrixH(r, n):
    H = []
    for i in range(r):
        H.append([])
        # base = middle number for carry
        base = math.pow(2,i)
        for j in range(n):
            # carry = n+1 % 2 to the power of r
            carry = (j+2) % math.pow(2,i+1)

            # zero = 1 to base
            # one = biger than base and 0
            if (carry <= base) and (carry != 0):
                H[i].append(0)
            else:
                H[i].append(1)             
    return H

def SwitchMatrixColumns(Matrix, SwitchList):
    M = deepcopy(Matrix)
    for switch in SwitchList:
        first = switch[0]
        second = switch[1]

        for i in range(len(M)):
            m_f = M[i][first]
            m_s = M[i][second]
            M[i][first] = m_s
            M[i][second] = m_f
    return M        

def TransposeMatrix(Matrix):
    M = deepcopy(Matrix)
    n = len(M)
    m = len(M[0])
    M_transpose = []
    for l in range(m):
        M_transpose.append([])
    for i in range(n):
        for j in range(m):
            M_transpose[j].append(M[i][j])
    return M_transpose        

def CalculateMinusMatrix(Matrix, q):
    M = deepcopy(Matrix)
    n = len(M)
    m = len(M[0])
    for i in range(n):
        for j in range(m):
            M[i][j] = (q - M[i][j]) % q
    return M

def FindMatrixA(r):
    
    n = int(math.pow(2, r)) - 1
    k = n - r

    H = BuildMatrixH(r, n)

    '''
    for a in range(r):
        column_num = n-r+a
        if H[a][column_num] == 0:
            for b in range(a+1, r):
                if H[b][column_num] == 1:
                    H = SwitchMatrixRows(H, (a, b))
                    break
                if b == k-1:
                    ...
                    # print("can't switch rows in H")
        H = GaussianElimination(H, a, n-r-1)
        
    '''
    switch_list = []
    for i in range(r):
        # second column = number of columns which forms I
        first_column = n-r+i
        second_column = int(math.pow(2, i)) - 1
        switch_list.append((first_column, second_column))

    H = SwitchMatrixColumns(H, switch_list)
    
    switch_list = []

    minus_A_transpose = []
    for j in range(r):
        minus_A_transpose.append(H[j][:n-r])

    A_transpose = CalculateMinusMatrix(minus_A_transpose, 2)
    A = TransposeMatrix(A_transpose)

    return A, H, switch_list

def BinaryAddition(N1, N2):
    sum = []
    for i in range(len(N1)):
        if (N1[i] == 1 and N2[i] == 1) or (N1[i] == 0 and N2[i] == 0):
            sum.append(0)
        else:
            sum.append(1)    
    return sum        

def SwitchMatrixRows(Matrix, SwitchTuple):
    M = deepcopy(Matrix)
    first_r = M[SwitchTuple[0]]
    second_r = M[SwitchTuple[1]]
    M[SwitchTuple[0]] = second_r
    M[SwitchTuple[1]] = first_r
    return M

def GaussianElimination(Matrix, base, ColumnNum):
    M = deepcopy(Matrix)
    for i in range(len(M)):
        if i != base and M[i][base + ColumnNum] == 1:
            sum = BinaryAddition(M[base], M[i])
            M[i] = sum
    return M

def BuildMatrixG(r, A, SwitchList):
    n = int(math.pow(2, r)) - 1
    k = n - r

    I = []
    for i in range(k):
        I.append([])
        for j in range(k):
            if i == j:
                I[i].append(1)
            else:
                I[i].append(0)

    G = []
    for l in range(k):
        G.append(I[l]+A[l])
    
    return G    
  




def MatrixMultiplyByModulusQ(Matrix1, Matrix2, q):
    M1 = deepcopy(Matrix1)
    M2 = deepcopy(Matrix2)
    rows1 = len(M1)
    columns1 = len(M1[0])
    rows2 = len(M2)
    columns2 = len(M2[0])
      
    if columns1 != rows2:
        # print("impossible equation")
        return None

    result = []
    for a in range(rows1):
        result.append([])
        for b in range(columns2):
            result[a].append(0)

    for i in range(rows1):
        for j in range(columns2):
            for k in range(columns1):
                result[i][j] = (result[i][j] + (M1[i][k] * M2[k][j])) % q

    return result

def FormGeneratorString(G, BinaryString, k):
    string = ""
    for i in range(0, len(BinaryString), k):
        k_part = BinaryString[i:i+k]
        extra_zero = 0
        if len(k_part) < k:
            extra_zero = k - len(k_part)
            k_part = k_part + ("0" * extra_zero)

        k_part_list = [[]]    
        for a in k_part:
            k_part_list[0].append(int(a))  
        Multiply_result = MatrixMultiplyByModulusQ(k_part_list, G, 2)

        Multiply_string = ""
        for b in Multiply_result[0]:
            Multiply_string = Multiply_string + str(b)      
        string = string + Multiply_string
    return string, extra_zero

def InsertRandomErorr(String, Error):
    length = len(String)
    # error_list = random.choices((0,1), [1-Error, Error], k=length)
    error_list = num_random.binomial(n=1, p=Error, size=length)

    input_list = []
    for s in String:
        input_list.append(int(s))
    result = BinaryAddition(input_list, error_list) 
    result_string = ""
    for r in result:
        result_string += str(r) 
      
    return result_string

def FindErorr(String, H, r):
    n = int(math.pow(2, r)) - 1

    for i in range(0, len(String), n):
        bit1 = []
        for j in range(n):
            if String[i:i+n][j] == "1":
                bit1.append(j+1)

        matrix_sum = []
        for a in range(r):
            matrix_sum.append([])  

        for b in bit1:
            for c in range(r):
                matrix_sum[c].append(H[c][b-1])
 
        for l in range(r):
            matrix_sum[l] = sum(matrix_sum[l]) % 2
   
        index = 0    
        for d in range(len(matrix_sum)):
            if matrix_sum[d] == 1:
                index += int(math.pow(2, d))
   
        if index != 0:
            if String[i+index-1] == "0":
                String = String[:i+index-1] + "1" + String[i+index:]
            else:
                String = String[:i+index-1] + "0" + String[i+index:]
   
    return String                
            
    

def RetriveSourceString(String, n, k, ExtraZero):
    result_string = ""
    for i in range(0, len(String), n):
        result_string += String[i:i+k]
    result_string = result_string[:len(result_string) - ExtraZero]   
    return result_string 

def OneErrorInEveryNbit(String, n):
    for i in range(0,len(String),n):
        num = random.randint(1,n)
        if String[i+num-1] == "0":
            String = String[:i+num-1] + "1" + String[i+num:]
        else:
            String = String[:i+num-1] + "0" + String[i+num:]
    return String        




def plot_xy(xy_tuple: list[tuple[float, float]], shannon_p: float = None):
    import matplotlib.pyplot as plt

    x = [pair[0] for pair in xy_tuple]
    y = [pair[1] for pair in xy_tuple]
    # print(x, y)
    # plt.plot(x, y,linestyle='None', marker='o', color='blue')
    # plt.axvline(x=((1 - shannon_p)/shannon_p), color='red', linestyle='--', linewidth=2, label=f'Threshold p*={shannon_p:.4f}')
    # plt.xscale('log')
    # plt.yscale('log')


    # # plt.xlim(min(x), min(y))

    # plt.xlabel("(1 - p)/p")
    # plt.ylabel("P_error")
    # plt.title("Graph of P_error vs (1 - p)/p")
    # plt.grid(True)
    # plt.legend()
    # plt.show()
    # plt.figure(figsize=(14, 6))
    plt.plot(x, y, marker='o')
    plt.title('Error Rate vs Bit Flip Probability')
    plt.ylabel('Rrror Rate')
    plt.xlabel('(1-p)/p')
    plt.xscale('symlog')
    plt.yscale('symlog', linthresh=1e-3)
    plt.grid()
    plt.axvline(
        x=(1 - shannon_p) / shannon_p, color="r", linestyle="--", label="x = 3/4"
    )
    plt.show()

def solve_for_p(r):
    def H(p):
        if p <= 0 or p >= 1:
            return 0.0
        return p * np.log2(p) + (1 - p) * np.log2(1 - p)

    n = 2 ** r - 1
    k = n - r
    C = k / n

    return root_scalar(lambda p: 1 + H(p) - C, bracket=[1e-10, 0.5 - 1e-10]).root



S = [("a", 0.2), ("b", 0.2), ("c", 0.1), ("d", 0.3), ("e", 0.2)]
length = 1000# int(input(f"enter length of the string on language S:"))
sorted_S = sorted(S, key=lambda x: x[1], reverse=True)

source_string = GenerateRandomSourceString(sorted_S, length)
binary_source_string, source_code = IncodeByHuffman(source_string, sorted_S) 

r = 5 #int(input(f"Enter redundancy:"))
n = int(math.pow(2, r)) - 1
k = n - r
shannon_possibility = solve_for_p(r)

A, H, swich_list = FindMatrixA(r) 
G = BuildMatrixG(r, A, swich_list)  

error_range = np.linspace(1e-5, .49, 100)
# error_range = [max(1e-6, p) for p in error_range]
changes = []
# for z in range(1,51):
for z in error_range:
    binary_generator_string, extra_zero = FormGeneratorString(G, binary_source_string, k)
    # error = float(input(f"enter Error probability:"))
    error = z#/100
    bugged_string = InsertRandomErorr(binary_generator_string, error)
    # bugged_string = OneErrorInEveryNbit(binary_generator_string, n)
    debugged_string = FindErorr(bugged_string, H, r)
    retrived_source_string = RetriveSourceString(debugged_string, n, k, extra_zero)

    count = 0
    for f in range(len(binary_source_string)):
        if binary_source_string[f] != retrived_source_string[f]:
            count += 1

    x = (1 - error) / error
    y = count / len(binary_source_string)
    changes.append((x, y))
    # print(x,y)
plot_xy(changes, shannon_possibility)    