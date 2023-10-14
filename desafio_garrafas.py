T = int(input())

for i in range(T):
    N, K = map(int, input().split())
    if N >= K:
        K = (N // K) + (N % K)
    else:
        K = N
    print(K)
