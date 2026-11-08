
define amdgpu_kernel void @atomic_or_ret_gds() {
  %val = atomicrmw or ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
