
define <10 x i64> @bitcast_v20i32_to_v10i64(<20 x i32> %a, i1 %cmp, <10 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <10 x i64> %0, splat (i64 1)
  ret <10 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <20 x i32> %a to <10 x i64>
  ret <10 x i64> %a3
}
