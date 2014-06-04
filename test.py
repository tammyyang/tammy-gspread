#!/usr/bin/env python

import numpy as np

def create_matrix(input_min, input_max):
    input_range_list = range(input_min, input_max+1)
    nelement = len(input_range_list)
    _x = np.zeros((nelement, nelement))

    for i in range(0, len(input_range_list)):
        _x[i][i] = input_range_list[i]

    return _x


def get_product(num_matrix, dimension):
    tmp = np.copy(num_matrix)
    for i in range(1, dimension):
        tmp = tmp.dot(num_matrix)
    return tmp.diagonal()

num_matrix = create_matrix(0, 5)
final_result = get_product(num_matrix, 3)
print final_result
#OR the following method
a = [0, 1, 2, 3, 4, 5]
final_result = [ a*b*c for a,b,c in zip(a,a,a)]
print final_result
