
define <15 x double> @bitcast_v30i32_to_v15f64(<30 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <30 x i32> %a, splat (i32 1)
  %a2 = bitcast <30 x i32> %a1 to <15 x double>
  ret <15 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <30 x i32> %a to <15 x double>
  ret <15 x double> %a3
}
