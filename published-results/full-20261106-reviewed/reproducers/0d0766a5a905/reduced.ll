
define amdgpu_kernel void @test_clmul_i32(i32 %b) {
  %res = call i32 @llvm.clmul.i32(i32 0, i32 %b)
  store i32 %res, ptr addrspace(1) null, align 4
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.clmul.i32(i32, i32) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
