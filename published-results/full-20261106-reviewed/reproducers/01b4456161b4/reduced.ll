
define <13 x i64> @bitcast_v26i32_to_v13i64(<26 x i32> %a, i1 %cmp, <13 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <13 x i64> %0, splat (i64 1)
  ret <13 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <26 x i32> %a to <13 x i64>
  ret <13 x i64> %a3
}
