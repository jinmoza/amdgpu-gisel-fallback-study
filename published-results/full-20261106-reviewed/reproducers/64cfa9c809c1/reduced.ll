
define float @copysign_known_signmask_f32_known_positive_mag_through_fence(float %sign.bit.known.zero) {
  %fence = call float @llvm.arithmetic.fence.f32(float %sign.bit.known.zero)
  ret float %fence
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.arithmetic.fence.f32(float) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
