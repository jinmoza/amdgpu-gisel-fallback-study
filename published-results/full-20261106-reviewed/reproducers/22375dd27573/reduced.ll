
define <7 x double> @bitcast_v14i32_to_v7f64(<14 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <14 x i32> %a, splat (i32 1)
  %a2 = bitcast <14 x i32> %a1 to <7 x double>
  ret <7 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <14 x i32> %a to <7 x double>
  ret <7 x double> %a3
}
