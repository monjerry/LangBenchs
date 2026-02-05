import random

random.seed(42)
inside = 0
n = 10_000_000
for _ in range(n):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
        inside += 1
