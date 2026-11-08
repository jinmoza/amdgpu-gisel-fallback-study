
define float @test_pow_afn_nnan_f32_known_integral_uitofp_i256(i256 %y) {
  %y.cast = uitofp i256 %y to float
  ret float %y.cast
}
