n = int(input())
spf = [i for i in range(n)]
for i in range(2, n):
    if spf[i] < i:
        continue
    print(i)
    for j in range(2 * i, n, i):
        spf[j] = min(spf[j], i)
