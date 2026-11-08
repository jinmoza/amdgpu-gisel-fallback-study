
define i32 @v1i8(<1 x i8> %x) {
  %y = call i32 @llvm.experimental.cttz.elts.i32.v1i8(<1 x i8> %x, i1 false)
  ret i32 %y
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.experimental.cttz.elts.i32.v1i8(<1 x i8>, i1 immarg) #0

attributes #0 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
