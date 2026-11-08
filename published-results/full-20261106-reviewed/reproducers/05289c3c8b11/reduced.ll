
define <15 x i64> @bitcast_v30i32_to_v15i64(<30 x i32> %a, i1 %cmp, <15 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <15 x i64> %0, splat (i64 1)
  ret <15 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <30 x i32> %a to <15 x i64>
  ret <15 x i64> %a3
}
