
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i68 @llvm.fshl.i68(i68, i68, i68) #0

define i68 @fshl_i68(i68 %amt) {
  %result = call i68 @llvm.fshl.i68(i68 1, i68 0, i68 %amt)
  ret i68 %result
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
