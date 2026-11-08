
define ptr addrspace(3) @atomic_load_p3(ptr addrspace(2) %ptr) {
  %val = load ptr addrspace(3), ptr addrspace(2) %ptr, align 4
  ret ptr addrspace(3) %val
}
