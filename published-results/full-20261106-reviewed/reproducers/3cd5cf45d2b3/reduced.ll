
define <11 x i64> @bitcast_v22i32_to_v11i64(<22 x i32> %a, i1 %cmp, <11 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <11 x i64> %0, splat (i64 1)
  ret <11 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <22 x i32> %a to <11 x i64>
  ret <11 x i64> %a3
}
