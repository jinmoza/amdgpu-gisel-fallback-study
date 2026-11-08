
define double @atomic_load_f64(ptr addrspace(2) %ptr) {
  %val = load double, ptr addrspace(2) %ptr, align 8
  ret double %val
}
