
define <13 x double> @bitcast_v26i32_to_v13f64(<26 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <26 x i32> %a, splat (i32 1)
  %a2 = bitcast <26 x i32> %a1 to <13 x double>
  ret <13 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <26 x i32> %a to <13 x double>
  ret <13 x double> %a3
}
