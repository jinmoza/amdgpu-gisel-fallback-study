
define bfloat @atomic_load_bf16(ptr addrspace(2) %ptr) {
  %val = load atomic bfloat, ptr addrspace(2) %ptr seq_cst, align 2
  ret bfloat %val
}
