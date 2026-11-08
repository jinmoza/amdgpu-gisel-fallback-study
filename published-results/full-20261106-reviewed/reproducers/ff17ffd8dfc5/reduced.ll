
define <10 x double> @bitcast_v20i32_to_v10f64(<20 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <20 x i32> %a, splat (i32 1)
  %a2 = bitcast <20 x i32> %a1 to <10 x double>
  ret <10 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <20 x i32> %a to <10 x double>
  ret <10 x double> %a3
}
