
define <9 x i64> @bitcast_v18i32_to_v9i64(<18 x i32> %a, i1 %cmp, <9 x i64> %0) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %1
  %a2 = or <9 x i64> %0, splat (i64 1)
  ret <9 x i64> %a2

cmp.false:                                        ; preds = %1
  %a3 = bitcast <18 x i32> %a to <9 x i64>
  ret <9 x i64> %a3
}
