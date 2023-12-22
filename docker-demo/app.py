import numpy as np
import argparse

argparser = argparse.ArgumentParser(description='Process some integers.')
argparser.add_argument('-i', type=int, default=0,
                    help='a number')

a = argparser.parse_args().i
b = 5

c = a + b

print(f'{a} + {b} = {c}')

A = np.array([1, 2, 3])
B = np.array([4, 5, 6])

C = A + B

print(f'{A} + {B} = {C}')


print("Program finished")