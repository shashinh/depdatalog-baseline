\ Model Baseline
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  obj_p15
Subject To
 sumToOne_V0: V0_0 + V0_1 = 1
 sumToOne_V2: V2_0 + V2_1 = 1
 sumToOne_V1: V1_000 + V1_001 + V1_010 + V1_011 + V1_100 + V1_101 + V1_110
   + V1_111 = 1
 c_e57: V0_1 = 0.7
 c_e67: V2_1 = 0.8
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
 c_aux12: - V1_110 + aux12 = 0
 c_aux13: - V1_111 + aux13 = 0
 c_obj_p15: - aux12 - aux13 + obj_p15 = 0
 c_aux14: - V1_010 + aux14 = 0
 c_aux15: - V1_011 + aux15 = 0
 c_aux16: - V1_110 + aux16 = 0
 c_aux17: - V1_111 + aux17 = 0
 c_obj_p12: - aux14 - aux15 - aux16 - aux17 + obj_p12 = 0
 c_aux18: - V1_011 + aux18 = 0
 c_aux19: - V1_111 + aux19 = 0
 c_obj_p16: - aux18 - aux19 + obj_p16 = 0
 c_aux20: - V0_0 + aux20 = 0
 c_aux23: - V0_0 + aux23 = 0
 c_aux26: - V0_1 + aux26 = 0
 c_aux29: - V2_0 + aux29 = 0
 c_aux32: - V0_1 + aux32 = 0
 c_aux35: - V2_0 + aux35 = 0
 c_aux38: - V2_1 + aux38 = 0
 c_obj_p17: - aux22 - aux25 - aux28 - aux31 - aux34 - aux37 - aux40
   + obj_p17 = 0
 c_aux21: aux21 + [ - V1_011 * aux20 ] = 0
 c_aux22: aux22 + [ - V2_1 * aux21 ] = 0
 c_aux24: aux24 + [ - V1_111 * aux23 ] = 0
 c_aux25: aux25 + [ - V2_1 * aux24 ] = 0
 c_aux27: aux27 + [ - V1_011 * aux26 ] = 0
 c_aux28: aux28 + [ - V2_1 * aux27 ] = 0
 c_aux30: aux30 + [ - V0_1 * aux29 ] = 0
 c_aux31: aux31 + [ - V1_110 * aux30 ] = 0
 c_aux33: aux33 + [ - V1_110 * aux32 ] = 0
 c_aux34: aux34 + [ - V2_1 * aux33 ] = 0
 c_aux36: aux36 + [ - V0_1 * aux35 ] = 0
 c_aux37: aux37 + [ - V1_111 * aux36 ] = 0
 c_aux39: aux39 + [ - V0_1 * aux38 ] = 0
 c_aux40: aux40 + [ - V1_111 * aux39 ] = 0
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
 aux12 <= 1
 aux13 <= 1
 obj_p15 <= 1
 aux14 <= 1
 aux15 <= 1
 aux16 <= 1
 aux17 <= 1
 obj_p12 <= 1
 aux18 <= 1
 aux19 <= 1
 obj_p16 <= 1
 aux20 <= 1
 aux21 <= 1
 aux22 <= 1
 aux23 <= 1
 aux24 <= 1
 aux25 <= 1
 aux26 <= 1
 aux27 <= 1
 aux28 <= 1
 aux29 <= 1
 aux30 <= 1
 aux31 <= 1
 aux32 <= 1
 aux33 <= 1
 aux34 <= 1
 aux35 <= 1
 aux36 <= 1
 aux37 <= 1
 aux38 <= 1
 aux39 <= 1
 aux40 <= 1
 obj_p17 <= 1
End
