#!/usr/bin/python
#
#  Copyright 2002-2019 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

from pycompss.api.task import task
from pycompss.api.parameter import *

import os

def load_block(fi):
    b = []
    f = open(fi, 'r')
    for line in f:
        split_line = line.split(' ')
        r = []
        for num in split_line:
            r.append(float(num))
        b.append(r)
    f.close()
    return b


def store_block(b, fi, size):
    f = open(fi, 'w')
    for row in b:
        for j in range(size):
            num = row[j]
            f.write(str(num))
            if j < size - 1:
                f.write(' ')
        f.write('\n')


# ## TASK SELECTION ## #

@task(input_A=DIRECTORY_IN, input_B=DIRECTORY_IN, output_C=DIRECTORY_INOUT)
def multiply(input_A, input_B, output_C, fa, fb, fc, size):

    print(f"INPUT directories are: {input_A}, {input_B}, {output_C}")
    print(f"fa fb fc are: {fa}, {fb}, {fc}")

    a = load_block(os.path.join(input_A, fa))
    b = load_block(os.path.join(input_B, fb))
    c = load_block(os.path.join(output_C, fc))
    for i in range(size):
        for j in range(size):
            for k in range(size):
                c[i][j] += a[i][k] * b[k][j]
    store_block(c, os.path.join(output_C, fc), size)
    print(f"C stored at: {os.path.join(output_C, fc)}")

    print(f"A is: {a}")
    print(f"B is: {b}")
    print(f"C is: {c}")


