
define amdgpu_kernel void @combine_ftrunc_fnearbyint_f32(float %v) {
  %round = tail call float @llvm.nearbyint.f32(float %v)
  store float %round, ptr addrspace(1) null, align 4
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.nearbyint.f32(float) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
