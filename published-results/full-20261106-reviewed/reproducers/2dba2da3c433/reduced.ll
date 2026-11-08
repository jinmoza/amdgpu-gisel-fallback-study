
; Function Attrs: nocallback nofree nounwind willreturn
declare void @llvm.amdgcn.s.dcache.wb() #0

define amdgpu_kernel void @test_s_dcache_wb() {
  call void @llvm.amdgcn.s.dcache.wb()
  ret void
}

attributes #0 = { nocallback nofree nounwind willreturn }
