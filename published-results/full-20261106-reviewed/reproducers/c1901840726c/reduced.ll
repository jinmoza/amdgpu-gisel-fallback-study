
define i16 @atomic_load_i16(ptr addrspace(2) %ptr) {
  %val = load atomic i16, ptr addrspace(2) %ptr seq_cst, align 2
  ret i16 %val
}
