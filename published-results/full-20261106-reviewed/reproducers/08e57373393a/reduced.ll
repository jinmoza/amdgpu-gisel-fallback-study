
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.ctpop.i16(i16) #0

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 1024) i32 @llvm.amdgcn.workitem.id.x() #1

define amdgpu_kernel void @v_ctpop_add_chain_i16(ptr addrspace(1) %in0, ptr addrspace(1) %in1) {
  %tid = call i32 @llvm.amdgcn.workitem.id.x()
  %1 = zext i32 %tid to i64
  %in1.gep = getelementptr [2 x i8], ptr addrspace(1) %in1, i64 %1
  %in0.gep = getelementptr [2 x i8], ptr addrspace(1) %in0, i64 %1
  %val0 = load i16, ptr addrspace(1) %in0.gep, align 4
  %ctpop0 = call i16 @llvm.ctpop.i16(i16 %val0)
  %val1 = load i16, ptr addrspace(1) %in1.gep, align 4
  %ctpop1 = call i16 @llvm.ctpop.i16(i16 %val1)
  %add = add i16 %ctpop0, %ctpop1
  store i16 %add, ptr addrspace(1) null, align 4
  ret void
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
