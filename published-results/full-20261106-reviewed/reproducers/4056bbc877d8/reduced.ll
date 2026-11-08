
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.nearbyint.f64(double) #0

define amdgpu_kernel void @nearbyint_f64(double %in) {
entry:
  %0 = call double @llvm.nearbyint.f64(double %in)
  store double %0, ptr addrspace(1) null, align 8
  ret void
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
