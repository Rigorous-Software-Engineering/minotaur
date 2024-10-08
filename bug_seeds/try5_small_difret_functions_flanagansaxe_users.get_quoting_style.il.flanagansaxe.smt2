(set-info :smt-lib-version 2.6)
(set-logic QF_ABV)
(set-info :source |
Ivan Jager <aij+nospam@andrew.cmu.edu>

|)
(set-info :category "industrial")
(set-info :status sat)
(declare-fun mem_35_221 () (Array (_ BitVec 32) (_ BitVec 8)))
(declare-fun mem_35_217 () (Array (_ BitVec 32) (_ BitVec 8)))
(declare-fun t_216 () (_ BitVec 1))
(declare-fun t_215 () (_ BitVec 1))
(declare-fun t_214 () (_ BitVec 1))
(declare-fun t_213 () (_ BitVec 1))
(declare-fun t_212 () (_ BitVec 1))
(declare-fun t_211 () (_ BitVec 1))
(declare-fun t_210 () (_ BitVec 1))
(declare-fun t_209 () (_ BitVec 1))
(declare-fun t_208 () (_ BitVec 1))
(declare-fun t_207 () (_ BitVec 1))
(declare-fun t_206 () (_ BitVec 1))
(declare-fun t_205 () (_ BitVec 1))
(declare-fun t_204 () (_ BitVec 1))
(declare-fun t_203 () (_ BitVec 1))
(declare-fun t_202 () (_ BitVec 1))
(declare-fun t_201 () (_ BitVec 1))
(declare-fun t_200 () (_ BitVec 1))
(declare-fun t_199 () (_ BitVec 1))
(declare-fun t_198 () (_ BitVec 1))
(declare-fun t_197 () (_ BitVec 1))
(declare-fun t_196 () (_ BitVec 1))
(declare-fun t_195 () (_ BitVec 1))
(declare-fun t_194 () (_ BitVec 1))
(declare-fun t_193 () (_ BitVec 1))
(declare-fun t_192 () (_ BitVec 1))
(declare-fun t_191 () (_ BitVec 1))
(declare-fun t_190 () (_ BitVec 1))
(declare-fun t_189 () (_ BitVec 1))
(declare-fun t_188 () (_ BitVec 1))
(declare-fun t_187 () (_ BitVec 1))
(declare-fun t_186 () (_ BitVec 1))
(declare-fun t_185 () (_ BitVec 1))
(declare-fun t_184 () (_ BitVec 1))
(declare-fun t_183 () (_ BitVec 1))
(declare-fun t_182 () (_ BitVec 1))
(declare-fun ra_final_56_181 () (_ BitVec 32))
(declare-fun T_32t1_1590_178 () (_ BitVec 32))
(declare-fun T_32t2_1594_174 () (_ BitVec 32))
(declare-fun ra_final_56_168 () (_ BitVec 32))
(declare-fun T_32t1_1582_165 () (_ BitVec 32))
(declare-fun T_32t2_1586_161 () (_ BitVec 32))
(declare-fun ra_final_56_137 () (_ BitVec 32))
(declare-fun T_1t0_1597_134 () (_ BitVec 1))
(declare-fun T_32t5_1602_133 () (_ BitVec 32))
(declare-fun R_ZF_13_127 () (_ BitVec 1))
(declare-fun T_32t3_1610_105 () (_ BitVec 32))
(declare-fun T_32t1_1608_104 () (_ BitVec 32))
(declare-fun T_32t2_1614_98 () (_ BitVec 32))
(declare-fun ra0_57_95 () (_ BitVec 32))
(declare-fun R_EBP_0_64 () (_ BitVec 32))
(declare-fun R_ESP_1_61 () (_ BitVec 32))
(assert (let ((?v_0 (bvadd T_32t2_1614_98 (_ bv4 32)))) (= (_ bv1 1) (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (bvand (ite (= t_216 (bvand t_215 (_ bv1 1))) (_ bv1 1) (_ bv0 1)) (ite (= t_215 (bvand t_198 (bvor (bvand t_199 (bvand t_203 (bvand t_204 (bvand t_205 (bvand t_206 (_ bv1 1)))))) (bvand t_207 (bvand t_211 (bvand t_212 (bvand t_213 (bvand t_214 (_ bv1 1))))))))) (_ bv1 1) (_ bv0 1))) (ite (= t_214 (ite (= ra_final_56_137 ra_final_56_181) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_213 (ite (= ra_final_56_181 T_32t1_1590_178) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_212 (ite (= T_32t1_1590_178 (bvor (bvor (bvor (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1594_174 (_ bv0 32)))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1594_174 (_ bv1 32)))) (_ bv8 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1594_174 (_ bv2 32)))) (_ bv16 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1594_174 (_ bv3 32)))) (_ bv24 32)))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_211 (bvand t_209 (bvand t_210 (_ bv1 1)))) (_ bv1 1) (_ bv0 1))) (ite (= t_210 (ite (= T_32t2_1594_174 ?v_0) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_209 (bvand t_208 (_ bv1 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_208 (_ bv1 1)) (_ bv1 1) (_ bv0 1))) (ite (= t_207 (bvnot T_1t0_1597_134)) (_ bv1 1) (_ bv0 1))) (ite (= t_206 (ite (= ra_final_56_137 ra_final_56_168) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_205 (ite (= ra_final_56_168 T_32t1_1582_165) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_204 (ite (= T_32t1_1582_165 (bvor (bvor (bvor (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1586_161 (_ bv0 32)))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1586_161 (_ bv1 32)))) (_ bv8 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1586_161 (_ bv2 32)))) (_ bv16 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t2_1586_161 (_ bv3 32)))) (_ bv24 32)))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_203 (bvand t_201 (bvand t_202 (_ bv1 1)))) (_ bv1 1) (_ bv0 1))) (ite (= t_202 (ite (= T_32t2_1586_161 ?v_0) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_201 (bvand t_200 (_ bv1 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_200 (_ bv1 1)) (_ bv1 1) (_ bv0 1))) (ite (= t_199 T_1t0_1597_134) (_ bv1 1) (_ bv0 1))) (ite (= t_198 (bvand t_195 (bvand t_196 (bvand t_197 (_ bv1 1))))) (_ bv1 1) (_ bv0 1))) (ite (= t_197 (ite (= T_1t0_1597_134 ((_ extract 0 0) T_32t5_1602_133)) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_196 (ite (= T_32t5_1602_133 (concat (_ bv0 31) R_ZF_13_127)) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_195 (bvand t_192 (bvand t_193 (bvand t_194 (_ bv1 1))))) (_ bv1 1) (_ bv0 1))) (ite (= t_194 (_ bv1 1)) (_ bv1 1) (_ bv0 1))) (ite (= t_193 (ite (= R_ZF_13_127 (ite (= T_32t3_1610_105 (_ bv0 32)) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_192 (bvand t_189 (bvand t_190 (bvand t_191 (_ bv1 1))))) (_ bv1 1) (_ bv0 1))) (ite (= t_191 (ite (= T_32t3_1610_105 (bvor (bvor (bvor (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t1_1608_104 (_ bv0 32)))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t1_1608_104 (_ bv1 32)))) (_ bv8 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t1_1608_104 (_ bv2 32)))) (_ bv16 32))) (bvshl (concat (_ bv0 24) (select mem_35_217 (bvadd T_32t1_1608_104 (_ bv3 32)))) (_ bv24 32)))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_190 (ite (= T_32t1_1608_104 (bvadd T_32t2_1614_98 (_ bv8 32))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_189 (bvand t_188 (_ bv1 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_188 (bvand t_185 (bvand t_186 (bvand t_187 (_ bv1 1))))) (_ bv1 1) (_ bv0 1))) (ite (= t_187 (ite (= mem_35_217 (store (store (store (store mem_35_221 (bvadd T_32t2_1614_98 (_ bv3 32)) ((_ extract 7 0) (bvlshr R_EBP_0_64 (_ bv24 32)))) (bvadd T_32t2_1614_98 (_ bv2 32)) ((_ extract 7 0) (bvlshr R_EBP_0_64 (_ bv16 32)))) (bvadd T_32t2_1614_98 (_ bv1 32)) ((_ extract 7 0) (bvlshr R_EBP_0_64 (_ bv8 32)))) (bvadd T_32t2_1614_98 (_ bv0 32)) ((_ extract 7 0) R_EBP_0_64))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_186 (ite (= T_32t2_1614_98 (bvsub R_ESP_1_61 (_ bv4 32))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_185 (bvand t_183 (bvand t_184 (_ bv1 1)))) (_ bv1 1) (_ bv0 1))) (ite (= t_184 (ite (= ra0_57_95 (bvor (bvor (bvor (concat (_ bv0 24) (select mem_35_221 (bvadd R_ESP_1_61 (_ bv0 32)))) (bvshl (concat (_ bv0 24) (select mem_35_221 (bvadd R_ESP_1_61 (_ bv1 32)))) (_ bv8 32))) (bvshl (concat (_ bv0 24) (select mem_35_221 (bvadd R_ESP_1_61 (_ bv2 32)))) (_ bv16 32))) (bvshl (concat (_ bv0 24) (select mem_35_221 (bvadd R_ESP_1_61 (_ bv3 32)))) (_ bv24 32)))) (_ bv1 1) (_ bv0 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_183 (bvand t_182 (_ bv1 1))) (_ bv1 1) (_ bv0 1))) (ite (= t_182 (_ bv1 1)) (_ bv1 1) (_ bv0 1))) (bvand (bvnot (bvand t_192 (bvand t_193 (bvnot (_ bv1 1))))) (bvor (bvnot (bvand t_216 (_ bv1 1))) (ite (not (= ra0_57_95 ra_final_56_137)) (_ bv1 1) (_ bv0 1))))))))
(check-sat)
(exit)
