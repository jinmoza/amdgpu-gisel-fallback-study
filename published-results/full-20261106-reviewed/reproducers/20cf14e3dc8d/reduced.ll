
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i67 @llvm.fshl.i67(i67, i67, i67) #0

define i67 @fshl_i67(i67 %amt) {
  %result = call i67 @llvm.fshl.i67(i67 1, i67 0, i67 %amt)
  ret i67 %result
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
