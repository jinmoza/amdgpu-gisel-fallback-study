
define bfloat @v_fdiv_bf16(bfloat %x) {
  %fdiv = fdiv bfloat %x, 0.000000e+00
  ret bfloat %fdiv
}
