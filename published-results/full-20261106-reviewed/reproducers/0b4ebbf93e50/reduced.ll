
define i64 @sshlsat_i64(i64 %lhs) {
  %res = call i64 @llvm.sshl.sat.i64(i64 %lhs, i64 0)
  ret i64 %res
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.sshl.sat.i64(i64, i64) #0

attributes #0 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
