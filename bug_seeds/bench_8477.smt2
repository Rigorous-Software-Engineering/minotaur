(set-info :smt-lib-version 2.6)
(set-logic QF_BV)
(set-info :source |
 Patrice Godefroid, SAGE (systematic dynamic test generation)
 For more information: http://research.microsoft.com/en-us/um/people/pg/public_psfiles/ndss2008.pdf
|)
(set-info :category "industrial")
(set-info :status unsat)
(declare-fun T1_5 () (_ BitVec 8))
(declare-fun T1_7 () (_ BitVec 8))
(assert (let ((?v_0 ((_ zero_extend 24) (_ bv31 8))) (?v_3 ((_ sign_extend 24) (bvsub T1_5 (_ bv48 8))))) (let ((?v_5 (bvadd ?v_3 ?v_3)) (?v_2 (bvashr ?v_3 ?v_0))) (let ((?v_12 (bvor (bvadd ?v_2 ?v_2) (bvashr ?v_5 ?v_0))) (?v_11 (bvadd ?v_5 ?v_5))) (let ((?v_6 (bvadd ?v_11 ?v_3)) (?v_10 (bvand ?v_5 (_ bv0 32)))) (let ((?v_8 (bvadd ?v_6 ?v_6)) (?v_4 (bvsub T1_7 (_ bv48 8)))) (let ((?v_7 ((_ sign_extend 24) ?v_4))) (let ((?v_9 (bvadd ?v_8 ?v_7)) (?v_1 (bvashr ?v_2 ?v_0))) (and true (not (= (bvor (bvadd ?v_1 ?v_1) (bvashr ?v_12 ?v_0)) (_ bv0 32))) (bvsle T1_7 (_ bv57 8)) (bvsle (_ bv48 8) T1_7) (not (= T1_7 (_ bv0 8))) (not (= ?v_4 (_ bv0 8))) (bvule ?v_7 ?v_9) (bvule (bvsub T1_5 (_ bv49 8)) (_ bv8 8)) (= (bvand ?v_10 (_ bv0 32)) (_ bv0 32)) (bvule ?v_8 ?v_9) (bvsle T1_5 (_ bv57 8)) (bvsle (_ bv48 8) T1_5) (not (= T1_5 (_ bv13 8))) (not (= T1_5 (_ bv10 8))) (not (= T1_5 (_ bv9 8))) (not (= T1_5 (_ bv32 8))) (not (= T1_5 (_ bv0 8))) (= ?v_10 (_ bv0 32)) (bvule ?v_11 ?v_6) (bvule ?v_3 ?v_6) (bvule (_ bv0 32) ?v_3) (bvule (_ bv0 32) ?v_12))))))))))
(check-sat)
(exit)
