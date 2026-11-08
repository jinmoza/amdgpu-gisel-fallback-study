
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare bfloat @llvm.cos.bf16(bfloat) #0

define amdgpu_kernel void @cos_bf16() {
  %cos = call bfloat @llvm.cos.bf16(bfloat +qnan)
  store bfloat %cos, ptr addrspace(1) null, align 2
  ret void
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
