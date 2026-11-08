
define <11 x double> @bitcast_v22i32_to_v11f64(<22 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <22 x i32> %a, splat (i32 1)
  %a2 = bitcast <22 x i32> %a1 to <11 x double>
  ret <11 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <22 x i32> %a to <11 x double>
  ret <11 x double> %a3
}
