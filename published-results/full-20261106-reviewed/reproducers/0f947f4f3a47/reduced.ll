
; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.amdgcn.cluster.workgroup.max.flat.id() #0

define amdgpu_kernel void @test_workgroup_max_flat_id() {
  %id = call i32 @llvm.amdgcn.cluster.workgroup.max.flat.id()
  store i32 %id, ptr addrspace(1) null, align 4
  ret void
}

attributes #0 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
