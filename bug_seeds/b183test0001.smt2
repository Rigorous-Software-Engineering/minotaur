(set-info :smt-lib-version 2.6)
(set-logic QF_ABV)
(set-info :source |
Bit-vector benchmarks from Dawson Engler's tool contributed by Vijay Ganesh
(vganesh@stanford.edu).  Translated into SMT-LIB format by Clark Barrett using
CVC3.

|)
(set-info :category "industrial")
(set-info :status sat)
(declare-fun test () (Array (_ BitVec 32) (_ BitVec 8)))
(declare-fun malloced_3 () (Array (_ BitVec 32) (_ BitVec 8)))
(assert (= (select malloced_3 (_ bv0 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv1 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv2 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv3 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv4 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv5 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv6 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv7 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv8 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv9 32)) (_ bv0 8)))
(assert (= (select malloced_3 (_ bv10 32)) (_ bv0 8)))
(assert (let ((?v_0 (store (store (store (store (store (store (store (store (store (store (store malloced_3 (_ bv0 32) (select test (_ bv0 32))) (_ bv1 32) (select test (_ bv1 32))) (_ bv2 32) (select test (_ bv2 32))) (_ bv3 32) (select test (_ bv3 32))) (_ bv4 32) (select test (_ bv4 32))) (_ bv5 32) (select test (_ bv5 32))) (_ bv6 32) (select test (_ bv6 32))) (_ bv7 32) (select test (_ bv7 32))) (_ bv8 32) (select test (_ bv8 32))) (_ bv9 32) (select test (_ bv9 32))) (_ bv10 32) (select test (_ bv10 32))))) (= (concat (concat (concat (select ?v_0 (_ bv7 32)) (select ?v_0 (_ bv6 32))) (select ?v_0 (_ bv5 32))) (select ?v_0 (_ bv4 32))) (_ bv61267 32))))
(check-sat)
(exit)
