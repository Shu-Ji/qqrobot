import random
from ctypes import c_int32 as int32, c_uint32 as uint32


i = lambda k: h(g(t(k)))
l = lambda k: k < 20 and 1518500249 or (k < 40 and 1859775393 or (k < 60 and -1894007588 or -899497514))
o = lambda k, z: int32(k << z).value | int32(uint32(k).value >> (32 - z)).value


def t(A):
    l = len(A)
    k = ((l + 8) >> 6) + 1
    B = [0] * (k * 16)
    for z in range(l):
        B[z >> 2] |= ord(A[z]) << (24 - (z & 3) * 8)
    z += 1
    B[z >> 2] |= 128 << (24 - (z & 3) * 8)
    B[z >> 2] = int32(B[z >> 2]).value
    B[- 1] = l * 8
    return B


def g(N):
    K = N
    L = [0] * 80
    J = 1732584193
    I = -271733879
    H = -1732584194
    G = 271733878
    F = -1009589776
    for C in range(0, len(K), 16):
        E, D, B, A, k = J, I, H, G, F
        for z in range(80):
            if z < 16:
                L[z] = K[C + z]
            else:
                L[z] = o(L[z - 3] ^ L[z - 8] ^ L[z - 14] ^ L[z - 16], 1)
            M = u(u(o(J, 5), x(z, I, H, G)), u(u(F, L[z]), l(z)))
            F, G, H, I, J = G, H, o(I, 30), J, M
        J, I, H, G, F = u(J, E), u(I, D), u(H, B), u(G, A), u(F, k)
    return J, I, H, G, F


def x(z, k, B, A):
    z = int32(z).value
    k = int32(k).value
    B = int32(B).value
    A = int32(A).value
    if z < 20:
        return int32(k & B).value | int32(int32(~k).value & A).value
    if z < 40:
        return int32(k ^ B ^ A).value
    if z < 60:
        return int32(k & B).value | int32(k & A).value | int32(B & A).value
    return int32(k ^ B ^ A).value


def u(k, B):
    k = int32(k).value
    B = int32(B).value

    A = int32(k & 65535).value + int32(B & 65535).value
    A = int32(A).value

    z = int32(k >> 16).value + int32(B >> 16).value + int32(A >> 16).value
    z = int32(z).value
    return int32(z << 16).value | int32(A & 65535).value


def h(A):
    z = "0123456789abcdef"
    B = ''
    for k in range(len(A) * 4):
        B += z[(A[k >> 2] >> ((3 - k % 4) * 8 + 4)) & 15] + z[(A[k >> 2] >> ((3 - k % 4) * 8)) & 15]
    return B


def m(z):
    return i(z + '951413')


def sig(cookies):
    w = cookies['nonce']
    y = str(int(random.random() * 899999) + 100000)
    ret = dict(cnonce=y, sig=i(m(w) + y))
    ret.update(cookies)
    return ret
