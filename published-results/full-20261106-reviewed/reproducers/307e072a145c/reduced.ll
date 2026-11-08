
; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare i32 @llvm.get.fpmode.i32() #0

define i32 @func_fpmode_i32() {
  %fpmode = call i32 @llvm.get.fpmode.i32()
  ret i32 %fpmode
}

attributes #0 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
