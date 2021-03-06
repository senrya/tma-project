import matplotlib.pyplot as plt
from math import erfc, sqrt, exp
import numpy as np

EbN0_dB = []
loi = []
i = 0
while i <= 10:
    EbN0_dB.append(i)
    i += 1
for item in EbN0_dB:
    EbN0 = 10**(item/10)
    BER = 1/2*exp(-EbN0)
    loi.append(BER)

plt.semilogy(EbN0_dB, loi,'m-s', label = "DPSK")
plt.legend()

plt.grid(True)
plt.ylabel('BER')
plt.xlabel('E_b/N_0 (dB)')
plt.title('Bit Error Rate for Differential Phase Shift Keying')
plt.show()


