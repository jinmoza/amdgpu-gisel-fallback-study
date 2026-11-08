
; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.stackrestore.p5(ptr addrspace(5)) #0

define amdgpu_kernel void @try_promote_unhandled_intrinsic() {
bb:
  call void @llvm.stackrestore.p5(ptr addrspace(5) null)
  ret void
}

attributes #0 = { nocallback nofree nosync nounwind willreturn }
