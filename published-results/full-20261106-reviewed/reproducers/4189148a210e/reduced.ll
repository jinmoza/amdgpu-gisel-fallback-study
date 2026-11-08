
define bfloat @log_bf16_ulp2() {
  %result = call bfloat @llvm.log.bf16(bfloat +qnan)
  ret bfloat %result
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare bfloat @llvm.log.bf16(bfloat) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
