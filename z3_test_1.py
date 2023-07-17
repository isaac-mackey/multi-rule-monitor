from z3 import *

s = Solver()
x2_f01 = Int('x2_f01')
x3_f11 = Int('x3_f11')

theta = And(If(And(x2_f01 >= 60), And(x2_f01 >= 60), True),
    x2_f01 >= 65,
    x3_f11 >= 65)

s.add(theta)
print("s.check()")
print(s.check())
print("s.model()")
print(s.model())