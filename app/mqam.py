import matplotlib.pyplot as plt
from math import erfc, sqrt, exp, log2
import numpy as np

EbN0_dB = []
loi_4 = []
loi_16 = []
loi_64 = []
i = 0
while i <= 24:
    EbN0_dB.append(i)
    i += 1
for item in EbN0_dB:
    EbN0 = 10**(item/10)
    k = log2(4)
    BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(4-1))))
    loi_4.append(BER)
for item in EbN0_dB:
    EbN0 = 10**(item/10)
    k = log2(16)
    BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(16-1))))
    loi_16.append(BER)
for item in EbN0_dB:
    EbN0 = 10**(item/10)
    k = log2(64)
    BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(64-1))))
    loi_64.append(BER)

plt.semilogy(EbN0_dB, loi_4, 'k-*', label = "4-QAM")
plt.semilogy(EbN0_dB, loi_16, 'g-o', label = "16-QAM")
plt.semilogy(EbN0_dB, loi_64, 'r-h', label = "64-QAM")
plt.ylim([10**-10,10])
plt.xlim([0,21])
plt.legend()
plt.grid(True)
plt.ylabel('BER')
plt.xlabel('E_b/N_0 (dB)')
plt.title('Bit Error Rate for Quadrature amplitude modulation')
plt.show()


