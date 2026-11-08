
define <7 x i64> @bitcast_v14i32_to_v7i64_scalar(i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  ret <7 x i64> splat (i64 1)

cmp.false:                                        ; preds = %0
  ret <7 x i64> zeroinitializer
}
