
define { bfloat, i16 } @frexp_nan_clamp_exp_bf16(bfloat %x) {
  %frexp = call { bfloat, i16 } @llvm.frexp.bf16.i16(bfloat %x)
  ret { bfloat, i16 } %frexp
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare { bfloat, i16 } @llvm.frexp.bf16.i16(bfloat) #0

attributes #0 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
