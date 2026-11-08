
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i66 @llvm.fshl.i66(i66, i66, i66) #0

define i66 @fshl_i66(i66 %amt) {
  %result = call i66 @llvm.fshl.i66(i66 1, i66 0, i66 %amt)
  ret i66 %result
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
