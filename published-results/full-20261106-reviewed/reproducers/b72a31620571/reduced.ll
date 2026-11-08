
define <7 x i64> @bitcast_v7f64_to_v7i64(<7 x double> %a) {
cmp.true:
  %a2 = bitcast <7 x double> %a to <7 x i64>
  ret <7 x i64> %a2
}
