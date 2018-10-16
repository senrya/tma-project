import matplotlib.pyplot as plt
from math import erfc, sqrt, exp, pi, sin, log2
import numpy as np

EbN0_dB = []
loi = []
i = 0
while i <= 10:
    EbN0_dB.append(i)
    i += 1
for item in EbN0_dB:
    EbN0 = 10**(item/10)
    k=log2(8);
    BER = 1/k*erfc(sqrt(EbN0*k)*sin(pi/8));
    loi.append(BER)

plt.semilogy(EbN0_dB, loi, "k-p", label = "8-PSK")
plt.legend()

plt.grid(True)
plt.ylabel('BER')
plt.xlabel('E_b/N_0 (dB)')
plt.title('Bit Error Rate for Quadature Phase Shift Keying')
plt.show()