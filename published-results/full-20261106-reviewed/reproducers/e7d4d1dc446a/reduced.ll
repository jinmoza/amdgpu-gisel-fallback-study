
define bfloat @sitofp_i12_to_bfloat(i12 %t1) {
  %c1 = sitofp i12 %t1 to bfloat
  ret bfloat %c1
}
