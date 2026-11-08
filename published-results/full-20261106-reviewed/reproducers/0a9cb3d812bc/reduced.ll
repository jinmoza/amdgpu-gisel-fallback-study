
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare bfloat @llvm.sin.bf16(bfloat) #0

define amdgpu_kernel void @sin_bf16() {
  %sin = call bfloat @llvm.sin.bf16(bfloat +qnan)
  store bfloat %sin, ptr addrspace(1) null, align 2
  ret void
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
