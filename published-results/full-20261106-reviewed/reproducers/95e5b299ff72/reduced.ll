
define <14 x i64> @bitcast_v28i32_to_v14i64(<28 x i32> %a, i1 %cmp, <14 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <14 x i64> %0, splat (i64 1)
  ret <14 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <28 x i32> %a to <14 x i64>
  ret <14 x i64> %a3
}
