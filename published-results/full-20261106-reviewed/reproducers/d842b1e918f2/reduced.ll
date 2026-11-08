
define ptr addrspace(2) @atomic_load_p2(ptr addrspace(2) %ptr) {
  %val = load ptr addrspace(2), ptr addrspace(2) %ptr, align 4
  ret ptr addrspace(2) %val
}
