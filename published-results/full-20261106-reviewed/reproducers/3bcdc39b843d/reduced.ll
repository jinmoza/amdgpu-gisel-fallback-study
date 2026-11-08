
define <12 x i64> @bitcast_v24i32_to_v12i64(<24 x i32> %a, i1 %cmp, <12 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <12 x i64> %0, splat (i64 1)
  ret <12 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <24 x i32> %a to <12 x i64>
  ret <12 x i64> %a3
}
