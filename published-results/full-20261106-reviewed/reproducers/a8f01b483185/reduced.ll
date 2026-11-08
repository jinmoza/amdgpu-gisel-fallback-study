
define half @atomic_load_f16(ptr addrspace(2) %ptr) {
  %val = load atomic half, ptr addrspace(2) %ptr seq_cst, align 2
  ret half %val
}
