
define <7 x double> @bitcast_v7i64_to_v7f64(<7 x i64> %a) {
cmp.true:
  %a2 = bitcast <7 x i64> %a to <7 x double>
  ret <7 x double> %a2
}
