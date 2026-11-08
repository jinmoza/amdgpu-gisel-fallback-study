
define half @v_fneg_arithmetic_fence_f16(half %a) {
  %fence = call half @llvm.arithmetic.fence.f16(half %a)
  ret half %fence
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare half @llvm.arithmetic.fence.f16(half) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
