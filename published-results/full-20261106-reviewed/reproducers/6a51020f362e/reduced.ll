
define amdgpu_kernel void @test_clmulr_i32(i64 %a.ext) {
  %clmul = call i64 @llvm.clmul.i64(i64 %a.ext, i64 0)
  %res = trunc i64 %clmul to i32
  store i32 %res, ptr addrspace(1) null, align 4
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.clmul.i64(i64, i64) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
