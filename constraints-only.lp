\ Model Baseline
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 sumToOne_V2: V2_0 + V2_1 = 1
 sumToOne_V0: V0_0 + V0_1 = 1
 sumToOne_V1: V1_000 + V1_001 + V1_010 + V1_011 + V1_100 + V1_101 + V1_110
   + V1_111 = 1
 c_e67: V2_1 = 0.8
 c_e57: V0_1 = 0.7
 c_e25: V1_100 + V1_101 + V1_110 + V1_111 = 0.6
 c_e12: V1_010 + V1_011 + V1_110 + V1_111 = 0.6
 c_e26: V1_001 + V1_011 + V1_101 + V1_111 = 0.6
 c_aux0: - V1_110 + aux0 = 0
 c_aux1: - V1_111 + aux1 = 0
 c_aux2: - 0.8 V1_100 + aux2 = 0
 c_aux3: - 0.8 V1_101 + aux3 = 0
 c_aux4: - 0.8 V1_110 + aux4 = 0
 c_aux5: - 0.8 V1_111 + aux5 = 0
 R14: - aux0 - aux1 + C18 = 0
 R15: - aux2 - aux3 - aux4 - aux5 + C18 = 0
 c_aux6: - V1_101 + aux6 = 0
 c_aux7: - V1_111 + aux7 = 0
 c_aux8: - 0.83 V1_100 + aux8 = 0
 c_aux9: - 0.83 V1_101 + aux9 = 0
 c_aux10: - 0.83 V1_110 + aux10 = 0
 c_aux11: - 0.83 V1_111 + aux11 = 0
 R22: - aux6 - aux7 + C25 = 0
 R23: - aux8 - aux9 - aux10 - aux11 + C25 = 0
Bounds
 V0_0 <= 1
 V0_1 <= 1
 V1_000 <= 1
 V1_001 <= 1
 V1_010 <= 1
 V1_011 <= 1
 V1_100 <= 1
 V1_101 <= 1
 V1_110 <= 1
 V1_111 <= 1
 V2_0 <= 1
 V2_1 <= 1
 aux0 <= 1
 aux1 <= 1
 aux2 <= 1
 aux3 <= 1
 aux4 <= 1
 aux5 <= 1
 C18 <= 1
 aux6 <= 1
 aux7 <= 1
 aux8 <= 1
 aux9 <= 1
 aux10 <= 1
 aux11 <= 1
 C25 <= 1
End
