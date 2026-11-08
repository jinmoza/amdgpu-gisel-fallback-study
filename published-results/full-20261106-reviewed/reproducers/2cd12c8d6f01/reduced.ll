
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i127 @llvm.fshl.i127(i127, i127, i127) #0

define i127 @fshl_i127(i127 %amt) {
  %result = call i127 @llvm.fshl.i127(i127 1, i127 0, i127 %amt)
  ret i127 %result
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
