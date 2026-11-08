
define float @atomic_load_f32(ptr addrspace(2) %ptr) {
  %val = load float, ptr addrspace(2) %ptr, align 4
  ret float %val
}
