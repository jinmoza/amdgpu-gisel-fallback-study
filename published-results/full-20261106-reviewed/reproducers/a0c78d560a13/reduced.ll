
define ptr addrspace(1) @atomic_load_p1(ptr addrspace(2) %ptr) {
  %val = load ptr addrspace(1), ptr addrspace(2) %ptr, align 8
  ret ptr addrspace(1) %val
}
