
define void @callbr_inline_asm() {
  callbr void asm "v_cmp_gt_i32_e64 vcc, $0, 42\0As_cbranch_vccnz ${1:l}", "r,!i"(i32 0)
          to label %common.ret [label %common.ret]

common.ret:                                       ; preds = %0, %0
  ret void
}
