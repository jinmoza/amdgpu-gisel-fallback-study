
define <14 x double> @bitcast_v28i32_to_v14f64(<28 x i32> %a, i1 %cmp) {
  br i1 %cmp, label %cmp.true, label %cmp.false

cmp.true:                                         ; preds = %0
  %a1 = or <28 x i32> %a, splat (i32 1)
  %a2 = bitcast <28 x i32> %a1 to <14 x double>
  ret <14 x double> %a2

cmp.false:                                        ; preds = %0
  %a3 = bitcast <28 x i32> %a to <14 x double>
  ret <14 x double> %a3
}
