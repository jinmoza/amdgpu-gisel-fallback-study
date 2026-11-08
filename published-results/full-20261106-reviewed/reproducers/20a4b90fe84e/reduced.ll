
define amdgpu_kernel void @non_uniform_loop() {
entry:
  br label %for.cond

for.cond:                                         ; preds = %for.cond, %entry
  %w = tail call i32 @llvm.amdgcn.workitem.id.x()
  %cmp.not = icmp eq i32 %w, 0
  br i1 %cmp.not, label %for.end, label %for.cond

for.end:                                          ; preds = %for.cond
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 1024) i32 @llvm.amdgcn.workitem.id.x() #0

attributes #0 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
