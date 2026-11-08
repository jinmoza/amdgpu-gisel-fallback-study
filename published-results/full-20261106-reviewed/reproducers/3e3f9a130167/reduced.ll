
; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i65 @llvm.fshl.i65(i65, i65, i65) #0

define i65 @fshl_i65(i65 %amt) {
  %result = call i65 @llvm.fshl.i65(i65 1, i65 0, i65 %amt)
  ret i65 %result
}

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
