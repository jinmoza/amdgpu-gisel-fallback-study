
define <12 x double> @bitcast_v24i32_to_v12f64(<24 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <24 x i32> %a, splat (i32 1)
  %a2 = bitcast <24 x i32> %a1 to <12 x double>
  ret <12 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <24 x i32> %a to <12 x double>
  ret <12 x double> %a3
}
