(set-info :smt-lib-version 2.6)
(set-logic QF_BV)
(set-info :source |
 Patrice Godefroid, SAGE (systematic dynamic test generation)
 For more information: http://research.microsoft.com/en-us/um/people/pg/public_psfiles/ndss2008.pdf
|)
(set-info :category "industrial")
(set-info :status unsat)
(declare-fun T1_387 () (_ BitVec 8))
(assert (and true (= T1_387 (_ bv82 8)) (not (= T1_387 (_ bv0 8))) (= T1_387 (_ bv110 8)) (not (= T1_387 (_ bv102 8))) (not (= T1_387 (_ bv116 8)))))
(check-sat)
(exit)
