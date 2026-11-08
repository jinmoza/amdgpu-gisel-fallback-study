
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare half @llvm.nearbyint.f16(half) #0

define amdgpu_kernel void @fnearbyint_f16(half %in) {
  %1 = call half @llvm.nearbyint.f16(half %in)
  store half %1, ptr addrspace(1) null, align 2
  ret void
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
